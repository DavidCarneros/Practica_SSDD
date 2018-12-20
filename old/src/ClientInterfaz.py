#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import IceStorm
import Ice
Ice.loadSlice('Downloader0.ice')
import DownloaderSlice
import time
import threading

class ProgressTopicI(DownloaderSlice.ProgressTopic):
    def timeStamp(self):
        return time.ctime(time.time())

    def notify(self, clipData, current=None):
        print("[{0}]: descarga: {1}".format(self.timeStamp(),clipData))

class Subscriber(Ice.Application):

    broker = None

    def descarga(self, argv, url):
        print(argv[1])
        proxy = broker.stringToProxy(argv[1])
        downloader = DownloaderSlice.DownloaderPrx.checkedCast(proxy)
        if not downloader:
            raise RuntimeError('Invalid proxy')
        print(downloader.download(url))
        return 0

    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property", key, "not set")
            return None

        print("Using IceStorm in: '%s'" % key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def create_topic(self, topic_mgr, topic_name):
        if not topic_mgr:
            print(': invalid proxy')
            return 2
        try:
            topic = topic_mgr.retrieve(topic_name)
            return topic
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)
            return topic

    def run(self,argv):
        global broker
        broker = self.communicator()
        topic_mgr = self.get_topic_manager()
        progress_topic = self.create_topic(topic_mgr,"ProgressTopic")

        servant = ProgressTopicI()
        adapter = broker.createObjectAdapter("ProgressTopicAdapter")
        subscriber = adapter.addWithUUID(servant)
        qos = {}

#        client = Client()
        progress_topic.subscribeAndGetPublisher(qos,subscriber)
        print("Waiting events... {}".format(subscriber))

        #download = threading.Thread(target=client.run, args=(sys.argv,self.broker,))
        download = threading.Thread(target = self.descarga, args=(sys.argv,"https://www.youtube.com/watch?v=PfU8xX-K9JY",))
        download.start()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        progress_topic.unsubscribe(subscriber)

if __name__ == '__main__':
    APP = Subscriber()
    APP.main(sys.argv)

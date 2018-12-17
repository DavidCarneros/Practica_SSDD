#!/usr/bin/python3
# -*- coding: utf-8 -*-
"usage: {} <server> <value>"

import sys
import threading
import Ice
import IceStorm
Ice.loadSlice('Downloader0.ice')
import DownloaderSlice

class ProgressTopicI(DownloaderSlice.ProgressTopic):
    def timeStamp(self):
        return time.ctime(time.time())

    def notify(self, clipData):
        print("[{0}]: descarga: {1}".format(self.timeStamp(),clipData))


class Client(Ice.Application):

    def hiloDownload(self, downloader_server, url):
        print(downloader_server.download(url))
        while 1:
            None
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

    def run(self, argv):
        base = self.communicator().stringToProxy(argv[1])
        broker = self.communicator()
    #    properties = broker.getProperties()
        downloader_server = DownloaderSlice.DownloaderPrx.checkedCast(base)

        if not downloader_server:
            raise RuntimeError("Invalid proxy")

        url = str(argv[2])
        #pylint: disable = E0602

    #    hilo1 = threading.Thread(target=self.hiloDownload, args=(downloader_server, url,))
    #    hilo1.start()
        #print(downloader_server.getSongsList())

        ''' Subscriber '''

        

        topic_mgr = self.get_topic_manager();
        qos = {}
        progress_topic = self.create_topic(topic_mgr,"ProgressTopic")
        identity = Ice.stringToIdentity("Cliente1")
        servant_progresstopic = ProgressTopicI()
        progresstopic_adapter = broker.createObjectAdapter("ProgressAdapter")
        subscriber_progresstopic = progresstopic_adapter.addWithUUID(servant_progresstopic)
        progress_topic.subscribeAndGetPublisher(qos, subscriber_progresstopic)
        progresstopic_adapter.activate()


        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        progress_topic.unsubscribe(subscriber_progresstopic)

        return 0


if len(sys.argv) != 4:
    print(__doc__.format(__file__))
    sys.exit(1)


app = Client()
sys.exit(app.main(sys.argv))

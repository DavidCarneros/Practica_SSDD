#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
import time
Ice.loadSlice('Downloader.ice')
import DownloaderSlice


class PrinterI(DownloaderSlice.SyncTopic):

    def timeStamp(self):
        return time.ctime(time.time())

    def requestSync(self, current=None):
        print("[{}] requestSync()".format(self.timeStamp()))
        sys.stdout.flush()
        
    def notify(self, songs_list, current=None):
        print("[{}], notify with songsList={}".format(self.timeStamp(),
            songs_list))

class Subscriber(Ice.Application):

    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property", key, "not set")
            return None

        print("Using IceStorm in: '%s'" % key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def run(self, argv):
        topic_mgr = self.get_topic_manager()
        if not topic_mgr:
            print (': invalid proxy')
            return 2

        ic = self.communicator()
        servant = PrinterI()
        adapter = ic.createObjectAdapter("PrinterAdapter")
        subscriber = adapter.addWithUUID(servant)

        topic_name = "SyncTopic"
        qos = {}
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)

        topic.subscribeAndGetPublisher(qos, subscriber)
        print ('Waiting events...', subscriber)

        adapter.activate()
        self.shutdownOnInterrupt()
        ic.waitForShutdown()

        topic.unsubscribe(subscriber)

        return 0


sys.exit(Subscriber().main(sys.argv))

#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
import time
Ice.loadSlice('downloader.ice')
import Downloader

class ProgressTopic(Downloader.ProgressEvent):

    def timeStamp(self):
        return time.ctime(time.time())

    def notify(self,clipdata,current=None):
        print("[{}] {}".format(self.timeStamp(),clipdata))

class SyncTopic(Downloader.SyncEvent):

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


        topic_mgr = self.get_topic_manager()
        qos = {}
        broker = self.communicator()
        ''' SyncTopic '''
        sync_topic = self.create_topic(topic_mgr,"SyncTopic")
        servant_syncTopic = SyncTopic()
        adapter = broker.createObjectAdapter("MonitorAdapter")
        subscriber_synctime = adapter.addWithUUID(servant_syncTopic)
        sync_topic.subscribeAndGetPublisher(qos, subscriber_synctime)
        print ('Waiting events...', subscriber_synctime)

        ''' ProgressTopic '''
        progress_topic = self.create_topic(topic_mgr,"ProgressTopic")
        servant_progressTopic = ProgressTopic()
        subscriber_progressTopic = adapter.addWithUUID(servant_progressTopic)
        progress_topic.subscribeAndGetPublisher(qos,subscriber_progressTopic)
        print ('Waiting events...', subscriber_progressTopic)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        sync_topic.unsubscribe(subscriber_synctime)

        return 0


sys.exit(Subscriber().main(sys.argv))

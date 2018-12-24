#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
import SyncTimer
Ice.loadSlice('downloader.ice')
import Downloader
import downloads_scheduler

class SchedulerFactoryI(Downloader.SchedulerFactory):

    schedulers = {}

    def __init__(self,publisher_synctime,publisher_progress,sync_topic):
        self.sync_topic = sync_topic
        self.publisher_progress = publisher_progress
        self.publisher_synctime = publisher_synctime

    def make(self, name, current=None):
        ''' Create schedulers '''
        if name in self.schedulers:
            raise Downloader.SchedulerAlreadyExists
        '''
        servant = downloads_scheduler0.DownloaderI(name,self.publisher_synctime,None)
        proxy = current.adapter.addWithUUID(servant)
        qos = {}
        self.sync_topic.subscribeAndGetPublisher(qos, proxy)
        self.schedulers[name]=proxy
        print("Waitings events...",proxy)
        '''
        servant = downloads_scheduler.DownloaderI(name,self.publisher_progress)
        schedure_proxy = current.adapter.addWithUUID(servant)

        servant_synctime = downloads_scheduler.SyncTimeI(self.publisher_synctime,servant)
        subscriber_synctime = current.adapter.addWithUUID(servant_synctime)
        qos = {}
        self.sync_topic.subscribeAndGetPublisher(qos, subscriber_synctime)
        self.schedulers[name]=schedure_proxy


        return Downloader.DownloadSchedulerPrx.checkedCast(schedure_proxy)

    def availableSchedulers(self,current=None):
        return len(self.schedulers)


class Server(Ice.Application):

    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        print(proxy)
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

        broker = self.communicator()
        properties = broker.getProperties()
        topic_mgr = self.get_topic_manager()
        qos = {}
        adapter = broker.createObjectAdapter("SchedulerFactoryAdapter")
        # Creacion del publisher para synctime
        sync_topic = self.create_topic(topic_mgr,"SyncTopic")
        publisher_synctime = Downloader.SyncEventPrx.uncheckedCast(sync_topic.getPublisher())

        # Creacion del publisher para progressTopic
        progress_topic = self.create_topic(topic_mgr,"ProgressTopic")
        publisher_progress = Downloader.ProgressEventPrx.uncheckedCast(progress_topic.getPublisher())

        servant_factory = SchedulerFactoryI(publisher_synctime,publisher_progress,sync_topic)
        #servant_factory = SchedulerFactoryI(None,None)

    #    proxy_factory = adapter.add(servant_factory, broker.stringToIdentity("SchedulerFactory1"))
        proxy_factory = adapter.add(servant_factory,Ice.stringToIdentity(properties.getProperty("Identity")))
        print(proxy_factory)


        sys.stdout.flush()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0

if __name__ == '__main__':
    server = Server()
    sys.exit(server.main(sys.argv))

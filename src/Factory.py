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

    def make(self, name, current=None):
        ''' Create schedulers '''
        if name in self.schedulers:
            raise Downloader.SchedulerAlreadyExists


        servant = downloads_scheduler.DownloaderI(name)
        schedure_proxy = current.adapter.addWithUUID(servant)
        self.schedulers[name]=schedure_proxy
        return Downloader.DownloadSchedulerPrx.checkedCast(schedure_proxy)

    def availableSchedulers(self,current=None):
        return len(self.schedulers)


class Server(Ice.Application):

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

        broker = self.communicator()
        properties = broker.getProperties()
        # factory
        servant_factory = SchedulerFactoryI()
        adapter = broker.createObjectAdapter("DownloaderFactoryAdapter")
    #    proxy_factory = adapter.add(servant_factory, broker.stringToIdentity("SchedulerFactory1"))
        proxy_factory = adapter.add(servant_factory,Ice.stringToIdentity(properties.getProperty("Identity")))
        print(proxy_factory)

        ''' Creacion del publisher y subscriber para el SyncTopic '''


        sys.stdout.flush()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0

if __name__ == '__main__':
    server = Server()
    sys.exit(server.main(sys.argv))

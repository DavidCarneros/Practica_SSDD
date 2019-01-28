#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

'''
Factoria encargado de crear los schedulers.

David Carneros Prado
3B
'''

import sys
import Ice
import IceStorm
import downloads_scheduler
#pylint: disable = E0401
#pyliny: disable = C0413
#pylint: disable = E1101
Ice.loadSlice('downloader.ice')
import Downloader


class SchedulerFactoryI(Downloader.SchedulerFactory):
    ''' Servant del factory '''


    def __init__(self, publisher_synctime, publisher_progress, sync_topic):
        self.sync_topic = sync_topic
        self.publisher_progress = publisher_progress
        self.publisher_synctime = publisher_synctime
        self.schedulers = {}
        self.subscriber_synctimers = {}

    def make(self, name, current=None):
        ''' Create schedulers '''
        if name in self.schedulers:
            raise Downloader.SchedulerAlreadyExists
        servant = downloads_scheduler.DownloaderI(name, self.publisher_progress)
        schedure_proxy = current.adapter.add(servant, Ice.stringToIdentity(name))
        servant_synctime = downloads_scheduler.SyncTimeI(self.publisher_synctime, servant)
        sync_timer_name = "{}_synctimer".format(name)
        subscriber_synctime = current.adapter.add(servant_synctime,Ice.stringToIdentity(sync_timer_name))
        qos = {}
        self.sync_topic.subscribeAndGetPublisher(qos, subscriber_synctime)
        self.schedulers[name] = schedure_proxy
        self.subscriber_synctimers["{}_synctimer".format(name)] = subscriber_synctime

        return Downloader.DownloadSchedulerPrx.checkedCast(schedure_proxy)

    def availableSchedulers(self, current=None):
        ''' Devuelve la cantidad de schedulers '''
        return len(self.schedulers)

    def kill(self, name, current=None):
        '''
        Elimina un scheduler creado
        '''
        sync_timer_name = "{}_synctimer".format(name)
        current.adapter.remove(Ice.stringToIdentity(name))
        self.sync_topic.unsubscribe(self.subscriber_synctimers[sync_timer_name])
        current.adapter.remove(Ice.stringToIdentity(sync_timer_name))
        del(self.schedulers[name])
        del(self.subscriber_synctimers[sync_timer_name])

class Server(Ice.Application):
    '''
    Factoria
    '''
    def get_topic_manager(self):
        ''' obtener el topic manager '''
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        print(proxy)
        if proxy is None:
            print("property", key, "not set")
            return None

        print("Using IceStorm in: '%s'" % key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def create_topic(self, topic_mgr, topic_name):
        ''' Crear el topic '''
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
        adapter = broker.createObjectAdapter(properties.getProperty("AdapterName"))
        # Creacion del publisher para synctime
        sync_topic = self.create_topic(topic_mgr, "SyncTopic")
        publisher_synctime = Downloader.SyncEventPrx.uncheckedCast(sync_topic.getPublisher())

        # Creacion del publisher para progressTopic
        progress_topic = self.create_topic(topic_mgr, "ProgressTopic")
        publisher_progress = Downloader.ProgressEventPrx.uncheckedCast(progress_topic.getPublisher())

        servant_factory = SchedulerFactoryI(publisher_synctime, publisher_progress, sync_topic)
        #servant_factory = SchedulerFactoryI(None,None)

    #    proxy_factory = adapter.add(servant_factory, broker.stringToIdentity("SchedulerFactory1"))
        proxy_factory = adapter.add(servant_factory, Ice.stringToIdentity(properties.getProperty("Identity")))
        print(proxy_factory)

        sys.stdout.flush()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0

if __name__ == '__main__':
    SERVER = Server()
    sys.exit(SERVER.main(sys.argv))

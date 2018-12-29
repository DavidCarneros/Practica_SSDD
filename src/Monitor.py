#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
'''
Monitor encargado de obtener las trazas de eventos de los
distintos topics

David Carneros Prado
3B
'''
import sys
import time
import Ice
import IceStorm
#pylint: disable = E0401
#pyliny: disable = C0413
#pylint: disable = C0413
#pylint: disable = E1101
Ice.loadSlice('downloader.ice')
import Downloader

class ProgressTopic(Downloader.ProgressEvent):
    ''' Servant del progressTopic '''
    def timestamp(self):
        '''
        Este metodo es usado para obtener las marcas de tiempo
        '''
        return time.ctime(time.time())

    def notify(self, clipdata, current=None):
        '''
        Cuando llegue un notify con el clipData lo mostraremos por pantalla
        junto a su marca de tiempo
        '''
        print("[{}] {}".format(self.timestamp(), clipdata))

class SyncTopic(Downloader.SyncEvent):
    '''
    Servatn del synctopic
    '''
    def timestamp(self):
        '''
        Este metodo es usado para obtener las marcas de tiempo
        '''
        return time.ctime(time.time())

    def requestSync(self, current=None):
        '''
        Cuando llegue un requestSync lo mostraremos por pantalla
        junto a su marca de tiempo
        '''
        print("[{}] requestSync()".format(self.timestamp()))
        sys.stdout.flush()

    def notify(self, songs, current=None):
        '''
        Cuando llegue un notify con la lista de canciones lo
        mostraremos por pantalla junto a su marca de tiempo
        '''
        print("[{}], notify with songsList={}".format(self.timestamp(), songs))

class Monitor(Ice.Application):
    ''' Encargado de mostrar la traza de eventos en los topics  '''

    def get_topic_manager(self):
        ''' obtener el topic manager '''
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
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

        topic_mgr = self.get_topic_manager()
        qos = {}
        broker = self.communicator()

        # SyncTopic
        sync_topic = self.create_topic(topic_mgr, "SyncTopic")
        servant_synctopic = SyncTopic()
        adapter = broker.createObjectAdapter("MonitorAdapter")
        subscriber_synctime = adapter.addWithUUID(servant_synctopic)
        sync_topic.subscribeAndGetPublisher(qos, subscriber_synctime)
        print('Waiting events...', subscriber_synctime)

        #ProgressTopic
        progress_topic = self.create_topic(topic_mgr, "ProgressTopic")
        servant_progresstopic = ProgressTopic()
        subscriber_progresstopic = adapter.addWithUUID(servant_progresstopic)
        progress_topic.subscribeAndGetPublisher(qos, subscriber_progresstopic)
        print('Waiting events...', subscriber_progresstopic)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        sync_topic.unsubscribe(subscriber_synctime)

        return 0


if __name__ == '__main__':
    sys.exit(Monitor().main(sys.argv))

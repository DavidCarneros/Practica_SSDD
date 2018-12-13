#!/usr/bin/pyhon3
# -*- coding: utf-8 -*-
''' Modulo SyncTimer '''
import sys
import time
import Ice
import IceStorm
#pylint: disable = E0401
#pyliny: disable = C0413
Ice.loadSlice("Downloader.ice")
import DownloaderSlice

KEY = 'IceStorm.TopicManager.Proxy'
TOPIC_NAME = 'SyncTopic'

class SyncTime(Ice.Application):
    '''
    Cada cierto tiempo mandara a la cola de eventos
    SyncTopic para que los servidores se sincronicen.
    '''
    def run(self, args):
        ''' Metodo run '''
        borker = self.communicator()

        topic_mgr_proxy = self.communicator().propertyToProxy(KEY)
        if topic_mgr_proxy is None:
            print("Property {0} not set".format(KEY))
            return 1
        #pylint ignore = E1101
        topic_mgr = IceStorm.TopicManagerPrx.checkedCast(topic_mgr_proxy)
        if not topic_mgr:
            print(": invalid proxy")
            return 2

        try:
            topic = topic_mgr.retrieve(TOPIC_NAME)
        except:
            topic = topic_mgr.create(TOPIC_NAME)

        publisher = DownloaderSlice.SyncTopicPrx.uncheckedCast(topic.getPublisher())

        counter = 0
        while True:
            counter += 1
            print("Sendig requestSync() numero: {}".format(counter))
            publisher.requestSync()
            time.sleep(7.5)

        return 0

if __name__ == '__main__':
    ''' Main del modulo'''
    APP = SyncTime()
    EXIT_STATUS = APP.main(sys.argv)
    sys.exit(EXIT_STATUS)

#!/usr/bin/pyhon3
# -*- coding: utf-8 -*-
''' Modulo SyncTimer '''
import sys
import Ice
import IceStorm
#pylint ignore = E0401
#pyliny ignore = C0413
Ice.loadSlice("Downloader.ice")
import Downloader

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

        publisher = Downloader.SyncTopicPrx.uncheckedCast(topic.getPublisher())

        while True:
            print("Sendig requestSync()")
            publisher.requestSync()

        return 0

if __name__ == '__main__':
    ''' Main del modulo'''
    APP = SyncTime()
    EXIT_STATUS = APP.main(sys.argv)
    sys.exit(EXIT_STATUS)

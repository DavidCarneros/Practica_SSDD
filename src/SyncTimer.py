#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
'''
Modulo SyncTimer

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
Ice.loadSlice("downloader.ice")
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
        broker = self.communicator()
        properties = broker.getProperties()
        topic_mgr_proxy = self.communicator().propertyToProxy(KEY)
        if topic_mgr_proxy is None:
            print("Property {0} not set".format(KEY))
            return 1
        #pylint: disable = E1101
        topic_mgr = IceStorm.TopicManagerPrx.checkedCast(topic_mgr_proxy)
        if not topic_mgr:
            print(": invalid proxy")
            return 2

        try:
            topic = topic_mgr.retrieve(TOPIC_NAME)
        except:
            topic = topic_mgr.create(TOPIC_NAME)

        publisher = Downloader.SyncEventPrx.uncheckedCast(topic.getPublisher())

        time_to_sleep = float(properties.getProperty("TimeToSleep"))
        counter = 0
        while True:
            counter += 1
            print("Sendig requestSync() numero: {}".format(counter))
            publisher.requestSync()
            time.sleep(time_to_sleep)

        return 0

if __name__ == '__main__':
    APP = SyncTime()
    EXIT_STATUS = APP.main(sys.argv)
    sys.exit(EXIT_STATUS)

#!/usr/bin/pyhon3
# -*- coding: utf-8 -*-
''' Modulo Server '''
import sys
import time
import Ice
import IceStorm
#pylint: disable = E0401
#pyliny: disable = C0413
Ice.loadSlice("Downloader.ice")
import DownloaderSlice

class SyncTime(DownloaderSlice.SyncTopic,DownloaderSlice.Downloader):
    def __init__ (self,publisher):
        self.publisher = publisher
        self.song_list = set([])

    def notify(self,song_list,current=None):
        conjunto_canciones = set(song_list)
        self.song_list = self.song_list.union(conjunto_canciones)


    def requestSync(self, current=None):
        print("requestSync")
        self.notify(list(self.song_list))
        sys.stdout.flush()

    def download_async(self,cb, url,current=None):
        print(url)
        cb.ice_response("recibido")
        sys.stdout.flush()

class Server(Ice.Application):

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

        topic_name = "SyncTopic"
        qos = {}
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)

        broker = self.communicator()
        publisherSyncTime = DownloaderSlice.SyncTopicPrx.uncheckedCast(topic.getPublisher())
        ic = self.communicator()
        servantSyncTime = SyncTime(publisherSyncTime)
        adapter = ic.createObjectAdapter("ServerAdapter")
        subscriberSyncTime = adapter.addWithUUID(servantSyncTime)
        topic.subscribeAndGetPublisher(qos, subscriberSyncTime)

        print ('Waiting events...', subscriberSyncTime)

        #### Parte del server descargas

        #servantDownload = DownloaderI()
        proxy = adapter.add(servantSyncTime, broker.stringToIdentity("server1"))
        print(proxy)
        adapter.activate()

        self.shutdownOnInterrupt()
        ic.waitForShutdown()

        topic.unsubscribe(subscriberSyncTime)

        return 0




sys.exit(Server().main(sys.argv))

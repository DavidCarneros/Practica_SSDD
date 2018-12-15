#!/usr/bin/pyhon3
# -*- coding: utf-8 -*-
''' Modulo Server '''
import sys
import Ice
import IceStorm
#pylint: disable = E0401
#pyliny: disable = C0413
Ice.loadSlice("Downloader.ice")
import DownloaderSlice


class SyncTime(DownloaderSlice.SyncTopic):
    ''' Servant del SyncTime '''
    def __init__ (self, publisher):
        ''' Constructor '''
        self.publisher = publisher
        self.song_list = set([])

    def notify(self, song_list, current=None):
        '''
         Modulo encargado de recibir el conjunto de canciones
        y juntarlo con el suyo, para asi actualizar la lista con
        todas las canciones de los servidores
         '''
        conjunto_canciones = set(song_list)
        self.song_list = self.song_list.union(conjunto_canciones)

    def requestSync(self, current=None):
        '''
        Modulo encargado de hacer el notify para enviar su lista
        de canciones y asi poder actualizarlas
        '''
        print("Llegada peticion de sincronizacion")
        self.notify(list(self.song_list))
        sys.stdout.flush()

class DownloaderI(DownloaderSlice.Downloader):
    ''' Servant del Downloader'''
    def __init__(self, sync_time):
        ''' Constructor '''
        self.sync_time = sync_time

    def download_async(self, call_back, url, current=None):
        '''
        Modulo asincrono encargado de recibir la url de la
        cancion que se tiene que descargar
        '''
        print("Recibida url: {}".format(url))
        call_back.ice_response("Recibida peticion de descarga")
        sys.stdout.flush()

    def getSongsList(self, current=None):
        '''
        Modulo encargado de mandar la lista de las canciones
        que tiene el servidor
        '''
        print("Envio de la lista de canciones al cliente")
        return list(self.SyncTime.song_list)

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
            print(': invalid proxy')
            return 2

        topic_name = "SyncTopic"
        qos = {}
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)

        broker = self.communicator()
        publisher_synctime = DownloaderSlice.SyncTopicPrx.uncheckedCast(topic.getPublisher())
        ic = self.communicator()
        servant_synctime = SyncTime(publisher_synctime)
        adapter = ic.createObjectAdapter("ServerAdapter")
        subscriber_synctime = adapter.addWithUUID(servant_synctime)
        topic.subscribeAndGetPublisher(qos, subscriber_synctime)

        print('Waiting events...', subscriber_synctime)

        #### Parte del server descargas

        servant_download = DownloaderI(servant_synctime)
        proxy = adapter.add(servant_download, broker.stringToIdentity("server1"))
        print(proxy)
        adapter.activate()

        self.shutdownOnInterrupt()
        ic.waitForShutdown()

        topic.unsubscribe(subscriber_synctime)

        return 0


if __name__ == '__main__':
    sys.exit(Server().main(sys.argv))

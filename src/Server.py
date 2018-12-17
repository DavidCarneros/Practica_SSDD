#!/usr/bin/pyhon3
# -*- coding: utf-8 -*-
''' Modulo Server '''
import sys
import Ice
import time
import IceStorm
#pylint: disable = E0401
#pyliny: disable = C0413
Ice.loadSlice("Downloader0.ice")
import DownloaderSlice
import work_queue



class SyncTime(DownloaderSlice.SyncTopic):
    ''' Servant del SyncTime '''
    def __init__ (self, publisher):
        ''' Constructor '''
        self.publisher = publisher
        self.song_list = set([])

    def timeStamp(self):
        return time.ctime(time.time())

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
        print("[{}] Llegada peticion de sincronizacion".format(self.timeStamp()))
        self.notify(list(self.song_list))
        sys.stdout.flush()
'''
class ProgressTopic(DownloaderSlice.ProgressTopic):
    def __init__(self,publisher):
        return 0
'''
class DownloaderI(DownloaderSlice.Downloader):
    ''' Servant del Downloader'''
    def __init__(self, sync_time, publisher_progresstopic):
        ''' Constructor '''
        self.sync_time = sync_time
        self.publisher_progress = publisher_progresstopic
        self.work_queue = work_queue.WorkQueue(self.publisher_progress)
        self.work_queue.start()



    def download_async(self, call_back, url, current=None):
        '''
        Modulo asincrono encargado de recibir la url de la
        cancion que se tiene que descargar
        '''
        print("Recibida url: {}".format(url))
        #call_back.ice_response("Recibida peticion de descarga")
        self.work_queue.add(call_back, url)


    def getSongsList(self, current=None):
        '''
        Modulo encargado de mandar la lista de las canciones
        que tiene el servidor
        '''
        print("Envio de la lista de canciones al cliente")
        return list(self.sync_time.song_list)

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
        '''
        RUN
        '''
        topic_mgr = self.get_topic_manager()
        qos = {}
        broker = self.communicator()
        properties = broker.getProperties()

        ''' Creacion del publisher y subscriber para el SyncTopic '''
        sync_topic = self.create_topic(topic_mgr,"SyncTopic")
        publisher_synctime = DownloaderSlice.SyncTopicPrx.uncheckedCast(sync_topic.getPublisher())
        identity = Ice.stringToIdentity(properties.getProperty("Identity"))
        servant_synctime = SyncTime(publisher_synctime)
        synctime_adapter = broker.createObjectAdapter("SyncAdapter")
        subscriber_synctime = synctime_adapter.addWithUUID(servant_synctime)
        sync_topic.subscribeAndGetPublisher(qos, subscriber_synctime)
        synctime_adapter.activate()

        print('Waiting events...', subscriber_synctime)

        ''' Creacion del publisher para el ProgressTopic '''

        ProgressTopic_topic = self.create_topic(topic_mgr,"ProgressTopic")
        publisher_progresstopic = DownloaderSlice.ProgressTopicPrx.uncheckedCast(ProgressTopic_topic.getPublisher())
        ProgressTopic_topic.subscribeAndGetPublisher(qos, subscriber_synctime)


        ''' Cracion del servant y el proxy para el download '''
        servant_download = DownloaderI(servant_synctime, publisher_progresstopic)
        download_adapter = broker.createObjectAdapter("DownloaderAdapter")
        identity = Ice.stringToIdentity(properties.getProperty("Identity"))
        proxy = download_adapter.add(servant_download, identity)
        print("\n {} \n".format(proxy))
        download_adapter.activate()


        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        sync_topic.unsubscribe(subscriber_synctime)

        return 0


if __name__ == '__main__':
    sys.exit(Server().main(sys.argv))

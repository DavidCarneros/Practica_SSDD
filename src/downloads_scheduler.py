#!/usr/bin/pyhon3
# -*- coding: utf-8 -*-
''' Modulo Server '''
import sys
import Ice
import time
import IceStorm
#pylint: disable = E0401
#pyliny: disable = C0413
Ice.loadSlice("downloader.ice")
import Downloader
import work_queue

class DownloaderI(Downloader.DownloadScheduler):
    ''' Servant del Downloader'''
    def __init__(self, name, publisher_progress=None):
        ''' Constructor '''
        self.name = name
        self.song_list = set([])
        self.publisher_progress = publisher_progress
        #self.publisher_progress = publisher_progresstopic
        self.work_queue = work_queue.WorkQueue(self)
        #self.work_queue = work_queue.WorkQueue(self.publisher_progress)
        self.work_queue.start()

    def addDownloadTask_async(self, call_back, url, current=None):
        '''
        Modulo asincrono encargado de recibir la url de la
        cancion que se tiene que descargar
        '''
        print("Recibida url: {}".format(url))
        #call_back.ice_response("Recibida peticion de descarga")
        self.work_queue.add(call_back, url)

    def getSongList(self, current=None):
        '''
        Modulo encargado de mandar la lista de las canciones
        que tiene el servidor
        '''
        print("Envio de la lista de canciones al cliente")
        return list(self.song_list)

class SyncTimeI(Downloader.SyncEvent):

    def __init__(self,publisher,servant):
        self.publisher = publisher
        self.servant = servant

    def notify(self, songs, current=None):
        '''
         Modulo encargado de recibir el conjunto de canciones
        y juntarlo con el suyo, para asi actualizar la lista con
        todas las canciones de los servidores
         '''
        self.servant.song_list = self.servant.song_list.union(set(songs))

    def requestSync(self, current=None):
        '''
        Modulo encargado de hacer el notify para enviar su lista
        de canciones y asi poder actualizarlas
        '''
        self.publisher.notify(list(self.servant.song_list))

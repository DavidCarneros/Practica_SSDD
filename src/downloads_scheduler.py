#!/usr/bin/pyhon3
# -*- coding: utf-8 -*-
#pylint: disable = W0613
'''
Modulo Scheduler
David Carneros Prado
Sistemas distribuidos
'''
import binascii
import Ice
import work_queue
#pylint: disable = E0401
#pyliny: disable = C0413
Ice.loadSlice("downloader.ice")
import Downloader


class DownloaderI(Downloader.DownloadScheduler):
    '''
    Servant del Downloader
    '''

    def __init__(self, name, publisher_progress=None):
        ''' Constructor '''
        self.name = name
        self.song_list = set([])
        self.publisher_progress = publisher_progress
        self.work_queue = work_queue.WorkQueue(self)
        self.work_queue.start()

    def addDownloadTask(self, url, current=None):
        '''
        Metodo asincrono encargado de recibir la url de la
        cancion que se tiene que descargar
        '''
        print("Recibida url: {}".format(url))
        #call_back.ice_response("Recibida peticion de descarga")
        self.work_queue.add(url)

    def getSongList(self, current=None):
        '''
        Metodo encargado de mandar la lista de las canciones
        que tiene el servidor
        '''
        print("Envio de la lista de canciones al cliente")
        return list(self.song_list)

    def cancelTask(self, url, current=None):
        '''
        Modulo encargado para cancelar una tarea de la workQueue
        '''
        print("no implementado")

    def get(self, song, current=None):
        '''
        Modulo para el envio de la cancion desde el directorio
        /tmp/dl/ a donde se este ejecutando el cliente
        '''
        dir_song = '/tmp/dl/{}'.format(song)
        proxy_transfer = current.adapter.addWithUUID(TransferI(dir_song))
        return Downloader.TransferPrx.checkedCast(proxy_transfer)

class SyncTimeI(Downloader.SyncEvent):
    '''
    Servant SyncTime
    '''

    def __init__(self, publisher, servant):
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

class TransferI(Downloader.Transfer):
    '''
    Transfer file
    '''
    def __init__(self, local_filename):
        self.file_contents = open(local_filename, 'rb')

    def recv(self, size, current=None):
        '''Send data block to client'''
        return str(
            binascii.b2a_base64(self.file_contents.read(size), newline=False)
        )

    def end(self, current=None):
        '''Close transfer and free objects'''
        self.file_contents.close()
        current.adapter.remove(current.id)

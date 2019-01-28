#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Modulo work_queue
David Carneros Prado
Sistemas distribuidos
'''

import queue
from threading import Thread
import Ice
# pylint: disable=C0413
Ice.loadSlice('downloader.ice')
# pylint: disable=E0401
import Downloader
import youtubedl




class NullLogger:
    '''
    Logger used to disable youtube-dl output
    '''
    def debug(self, msg):
        '''Ignore debug messages'''

    def warning(self, msg):
        '''Ignore warnings'''

    def error(self, msg):
        '''Ignore errors'''


# Default configuration for youtube-dl
DOWNLOADER_OPTS = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': NullLogger()
}


class WorkQueue(Thread):
    '''
    Clase workQueue que tendra una cola con los trabajos, es decir
    la url de la cancion que tiene que descargar.
    '''

    QUIT = 'QUIT'
    CANCEL = 'CANCEL'

    def __init__(self, servant):
        super(WorkQueue, self).__init__()
        self.queue = queue.Queue()
        self.servant = servant

    def run(self):
        for job in iter(self.queue.get, self.QUIT):
            job.download()
            self.queue.task_done()

        self.queue.task_done()
        self.queue.put(self.CANCEL)

        for job in iter(self.queue.get, self.CANCEL):
            job.cancel()
            self.queue.task_done()

        self.queue.task_done()

    def add(self, url):
        ''' Añadir un trabajo a la cola de trabajo '''
        self.queue.put(Job(url, self.servant))

    def destroy(self,url):
        ''' Quitar un trabajo de la cola de trabajo '''
        self.queue.put(self.QUIT)
        self.queue.join()


class Job(object):
    '''
    La clase Job sera el trabajo que se usara en la cola de trabajo.
    Es el encargado ademas de mandar el progreso al progressTopic
    '''
    def __init__(self, url, servant):
        self.servant = servant
        self.url = url
        self.clip_data = Downloader.ClipData(self.url, Downloader.Status.PENDING)
        self.servant.publisher_progress.notify(self.clip_data)

    def download(self):
        ''' Encargado de descargar el video '''
        self.clip_data.status = Downloader.Status.INPROGRESS
        self.servant.publisher_progress.notify(self.clip_data)
        youtube_dl = youtubedl.YoutubeDL("/tmp/dl")
        try:
            name = youtube_dl.download(self.url)
            self.clip_data.status = Downloader.Status.DONE
            self.servant.publisher_progress.notify(self.clip_data)
            self.servant.song_list.add(name[8:])
        #    self.callback.ice_response("Vídeo descargado: {0}".format(self.url))

        except:
            self.clip_data.status = Downloader.Status.ERROR
            self.servant.publisher_progress.notify(self.clip_data)
        #    self.callback.ice_response("Error al descargar: {0}".format(self.url))


    def cancel(self):
        '''Cancel donwload'''
    #    self.callback.ice_exception(Downloader.SchedulerCancelJob())

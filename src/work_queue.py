#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Sistemas Distribuidos
Nombre: Sergio Gonzalez Velazquez
DNI:71359610V
Curso: 2018 / 2019
"""

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

    def add(self, cb, url):
        self.queue.put(Job(cb, url,self.servant))

    def destroy(self):
        self.queue.put(self.QUIT)
        self.queue.join()


class Job(object):
    def __init__(self, callback, url,servant):
        self.servant = servant
        self.callback = callback
        self.url = url

        #self.publisher.notify((self.url,"none","none","Pending"))
        #self.publisher.notify("Pending")
        self.clipData = Downloader.ClipData(self.url,Downloader.Status.PENDING)
        self.servant.publisher_progress.notify(self.clipData)

    def download(self):
        #descargar el video de yourube
        self.clipData.status=Downloader.Status.INPROGRESS
        self.servant.publisher_progress.notify(self.clipData)

        youtube_dl = youtubedl.YoutubeDL("../dl")
        try:
            name = youtube_dl.download(self.url)
            self.clipData.status=Downloader.Status.DONE
            self.servant.publisher_progress.notify(self.clipData)

            #self.cb.ice_response(video)
            self.servant.song_list.add(name)
            print("añadido name",self.servant.song_list)
            self.callback.ice_response("Vídeo descargado: {0}".format(self.url))
        except:
            self.clipData.status=Downloader.Status.ERROR
            self.servant.publisher_progress.notify(self.clipData)
            self.callback.ice_response("Error al descargar: {0}".format(self.url))

    def cancel(self):
        '''Cancel donwload'''
        self.callback.ice_exception(Downloader.SchedulerCancelJob())

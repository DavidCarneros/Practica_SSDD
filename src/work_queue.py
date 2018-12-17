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
#Ice.loadSlice('Printer.ice')
# pylint: disable=E0401
import youtubedl
from Clip_Data import *

class WorkQueue(Thread):
    QUIT = 'QUIT'
    CANCEL = 'CANCEL'

    def __init__(self, publisher):
        super(WorkQueue, self).__init__()
        self.queue = queue.Queue()
        self.publisher = publisher

    def run(self):
        for job in iter(self.queue.get, self.QUIT):
            job.execute()
            self.queue.task_done()

        self.queue.task_done()
        self.queue.put(self.CANCEL)

        for job in iter(self.queue.get, self.CANCEL):
            job.cancel()
            self.queue.task_done()

        self.queue.task_done()

    def add(self, cb, url):
        self.queue.put(Job(cb, url,self.publisher))

    def destroy(self):
        self.queue.put(self.QUIT)
        self.queue.join()


class Job(object):
    def __init__(self, cb, url,publisher):
        self.cb = cb
        self.url = url
        self.publisher = publisher
        self.publisher.notify("Pending")
        #self.clipData = ClipData(str(self.url), "none", "none", Status.Pending)

    def execute(self):
        #descargar el video de yourube
        self.publisher.notify("InProgress")
        youtube_dl = youtubedl.YoutubeDL("../dl")
        try:
            youtube_dl.download(self.url)
            self.publisher.notify("Done")
            self.cb.ice_response("Vídeo descargado: {0}".format(self.url))
        except:
            self.publisher.notify("Error")
            self.cb.ice_response("Error al descargar: {0}".format(self.url))

    """
    def cancel(self):
        self.cb.ice_exception(Example.RequestCancelException())
    """

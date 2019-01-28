#!/usr/bin/python3
''' Modulo para la descarga de videos de youtube '''
from __future__ import unicode_literals
import youtube_dl
import os


ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

DL_INSTANCE = None

def my_hook(d):
    global DL_INSTANCE
    DL_INSTANCE.hook(d)

class DLLogger(object):
    ''' DLLogger'''
    def __init__(self, YDL):
        self.ydl = YDL

    def debug(self, msg):
        ''' debug '''
        prefix = msg.rfind('ffmpeg] Destination:')
        if (prefix == 1):
            filename = msg[prefix + 21:msg.rfind('mp3')+3]
            self.ydl.set_current_file(filename)

    def warning(self, msg):
        ''' print warning message '''
        print("warning: {}".format(msg))

    def error(self, msg):
        ''' print error message '''
        print("error: {}".format(msg))


class YoutubeDL:
    ''' Clase youtubeDL'''
    def __init__(self, target_folder):
        self.logger = DLLogger(self)
        self.params = ydl_opts
        self.params['logger'] = self.logger
        self.params['progress_hooks'] = [my_hook]
        self.params['outtmpl'] = target_folder + "/%(title)s-%(id)s.%(ext)s2"
        self.youtube_dl = youtube_dl.YoutubeDL(self.params)
        self.current_file = ''
        global DL_INSTANCE
        DL_INSTANCE = self

    def set_current_file(self, filename):
        ''' set_current_file '''
        self.current_file = filename

    def download(self, url):
        ''' download video'''
        self.current_file = ''
        self.youtube_dl.download([url])
        return self.current_file

    # esta función puede ser usada para implementar un callback de progreso
    def hook(self, msg):
        ''' esta función puede ser usada para implementar un callback de progreso '''
        print("{}%".format(round(msg['downloaded_bytes']/msg['total_bytes']*100)))

if __name__ == "__main__":

    DL = YoutubeDL('/tmp/dl')
    print(DL.download('https://www.youtube.com/watch?v=ioyNa3EdEVk'))

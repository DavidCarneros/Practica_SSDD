#!/usr/bin/python3
from __future__ import unicode_literals
import youtube_dl


ydl_opts = {    
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

dl_instance = None

def my_hook(d):
    global dl_instance
    dl_instance.hook(d)
        
class DLLogger(object):
    def __init__(self, YDL):
        self.ydl = YDL
        
    def debug(self, msg):
        prefix = msg.rfind('ffmpeg] Destination:')
        if (prefix == 1):
            filename = msg[prefix + 21:msg.rfind('mp3')+3]
            self.ydl.set_current_file(filename)
        
    def warning(self, msg):
        print("warning: {}".format(msg))        

    def error(self, msg):
        print("error: {}".format(msg))


class YoutubeDL:
    def __init__(self, target_folder):
        self.logger = DLLogger(self)
        self.params = ydl_opts
        self.params['logger'] = self.logger
        self.params['progress_hooks'] = [my_hook]
        self.params['outtmpl'] = "./" + target_folder + "/%(title)s-%(id)s.%(ext)s2"
        self.youtube_dl = youtube_dl.YoutubeDL(self.params)
        self.current_file = ''
        global dl_instance
        dl_instance = self

    def set_current_file(self, filename):
        self.current_file = filename
        
    def download(self, url):
        self.current_file = ''
        self.youtube_dl.download([url])
        return self.current_file

    # esta función puede ser usada para implementar un callback de progreso
    def hook(self, msg):        
        print("{}%".format(round(msg['downloaded_bytes']/msg['total_bytes']*100)))

if __name__ == "__main__":

    dl = YoutubeDL('dl')
    print(dl.download('https://www.youtube.com/watch?v=BaW_jenozKc'))

#!/usr/bin/python3
''' '''
import sys
import cmd
import Ice
Ice.loadSlice('downloader.ice')
import Downloader
import random

class Shell(cmd.Cmd):
    ''' '''
    client = None
    prompt = 'Downloader> '

    def __init__(self,client):
        super(Shell, self).__init__()
        self.client = client

    def emptyline(self):
        return

    def do_connect(self,line):
        '''Connect to proxy'''
        try:
            self.client.connect(line)
            self.prompt = 'Downloader(online)> '
        except:
            print("Error in conexion")
        return

    def do_getSongList(self,line):
        ''' '''
        song_list = self.client.getSongList()
        if song_list is []:
            print("No songs available")
        else:
            for song in song_list:
                print("{}".format(song))
        return

    def do_add_download(self,line):
        ''' '''
        self.client.add_download(line)
        return

    def do_create_schedule(self,line):
        ''' '''
        self.client.create_schedule(line)
        return

    def do_exit(self,line):
        '''End program execution '''
        return True


class Client(Ice.Application):
    ''' Ice application cliente  '''

    factory = None
    schedulers = {}

    def connect(self,proxy):
        proxy_factory = self.communicator().stringToProxy(proxy)
        self.factory = Downloader.SchedulerFactoryPrx.checkedCast(proxy_factory)
        print(self.factory)
        if not self.factory:
            raise RuntimeError('Invalid proxy')

    def create_schedule(self,name):
        if name in self.schedulers:
            raise Downloader.SchedulerAlreadyExists
        schedule = self.factory.make(name)
        self.schedulers[name]=schedule

    def getSongList(self):
        if len(self.schedulers) is 0:
            print("No schedulers create")
        else:
            key = random.choice(list(self.schedulers))
            songs = self.schedulers[key].getSongList()
            return songs

    def add_download(self,line):
        if len(self.schedulers) is 0:
            print("No schedulers create")
        else:
            key = random.choice(list(self.schedulers))
            self.schedulers[key].addDownloadTask(line)

    def run(self,argv):
        Shell(self).cmdloop()
        return 0


if __name__ == '__main__':
    APP = Client()
    sys.exit(APP.main(sys.argv))

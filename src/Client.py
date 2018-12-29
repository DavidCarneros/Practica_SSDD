#!/usr/bin/python3
''' '''
import sys
import cmd
import Ice
Ice.loadSlice('downloader.ice')
import Downloader
import IceStorm
import random
import pprint

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
    #    try:
        self.client.connect(line)
        self.prompt = 'Downloader(online)> '
    #    except:
        #    print("Error in conexion")
        return

    def do_connect_default(self,line=None):
        try:
            self.client.connect_default()
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

    def do_show_progress(self,line):
        self.client.show_progress()

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

class ProgressEventI(Downloader.ProgressEvent):
    def __init__(self,client):
        self.client=client

    def notify(self,clipData,current=None):
        if clipData.URL in self.client.downloads:
            self.client.downloads.update({clipData.URL:clipData.status})

class Client(Ice.Application):
    ''' Ice application cliente  '''

    factory = None
    schedulers = {}
    downloads = {}


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


    def connect(self,proxy):

        proxy_factory = self.communicator().stringToProxy(proxy)
        self.factory = Downloader.SchedulerFactoryPrx.checkedCast(proxy_factory)
        if not self.factory:
            raise RuntimeError('Invalid proxy')

        topic_mgr = self.get_topic_manager()
        progress_topic = self.create_topic(topic_mgr,"ProgressTopic")
        adapter = self.communicator().createObjectAdapter("ProgressAdapter")
        servanst_progress = ProgressEventI(self)
        subscriber_progress = adapter.addWithUUID(servant_progress)
        qos = {}
        progress_topic.subscribeAndGetPublisher(qos, subscriber_progress)
        adapter.activate()

    def connect_default(self):
        proxy = 'SchedulerFactory1 -t -e 1.1 @ DownloaderFactory.SchedulerFactoryAdapter'
        proxy_factory = self.communicator().stringToProxy(proxy)
        self.factory = Downloader.SchedulerFactoryPrx.checkedCast(proxy_factory)
        if not self.factory:
            raise RuntimeError('Invalid proxy')
        topic_mgr = self.get_topic_manager()
        progress_topic = self.create_topic(topic_mgr,"ProgressTopic")
        adapter = self.communicator().createObjectAdapter("ProgressAdapter")
        servant_progress = ProgressEventI(self)
        subscriber_progress = adapter.addWithUUID(servant_progress)
        qos = {}
        progress_topic.subscribeAndGetPublisher(qos, subscriber_progress)
        adapter.activate()


    def show_progress(self):
        pprint.pprint(self.downloads)


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
            self.downloads[line]=None
            self.schedulers[key].begin_addDownloadTask(line)

    def run(self,argv):
        Shell(self).cmdloop()
        return 0


if __name__ == '__main__':
    APP = Client()
    sys.exit(APP.main(sys.argv))

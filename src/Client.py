#!/usr/bin/python3
'''
cliente
David Carneros Prado
'''
import binascii
import sys
import cmd
import random
import pprint
import Ice
import IceStorm
#pylint: disable = E0401
#pyliny: disable = C0413
#pylint: disable = C0413
#pylint: disable = E1101
Ice.loadSlice('downloader.ice')
import Downloader

BLOCK_SIZE = 10240

class Shell(cmd.Cmd):
    ''' '''
    client = None
    prompt = 'Downloader> '

    def __init__(self, client):
        super(Shell, self).__init__()
        self.client = client

    def emptyline(self):
        return

    def do_connect(self, line):
        '''Connect to proxy'''
        try:
            self.client.connect(line)
            self.prompt = 'Downloader(online)> '
        except:
            print("Error in conexion")

        return

    def do_connect_default(self, line=None):
        '''
        Connect to the default factory proxy
        SchedulerFactory1 -t -e 1.1 @ DownloaderFactory.SchedulerFactoryAdapte
        '''
        try:
            self.client.connect_default()
            self.prompt = 'Downloader(online)> '
        except:
            print("Error in conexion")
        return

    def do_song_list(self, line):
        '''
        returns the list of downloaded songs
        '''
        song_list = self.client.getSongList()
        if song_list == []:
            print("No songs available")
        else:
            for song in song_list:
                print("{}".format(song))
        return

    def do_show_progress(self, line):
        '''
        Shows the download process
        '''
        self.client.show_progress()

    def do_add_download(self, line):
        '''
        Add a download to a random scheduler
        '''
        self.client.add_download(line)
        return

    def do_kill(self, line):
        '''
        Remove a scheduler
        '''
        try:
            self.client.kill(line)
        except Downloader.SchedulerNotFound:
            print("The scheduler: {} does not exist".format(line))

    def do_create_schedule(self, line):
        '''
        Create a scheduler
        '''
        try:
            self.client.create_schedule(line)
            print("Schedule create with the name {}".format(line))
        except Downloader.SchedulerAlreadyExists:
            print("Scheduler Already Exists")
        return

    def do_get_song(self, line):
        '''
        Get the downloaded song and save it in the current directory
        '''
        self.client.getFile(line)
        return

    def do_schedulers_avalible(self, line):
        '''
        Returns the number of active schedulers in the factory
        '''
        print(self.client.availableSchedulers())
        return

    def do_exit(self, line):
        '''End program execution '''
        self.client.killAll();
        return True

class ProgressEventI(Downloader.ProgressEvent):
    '''
    Servant del progressEvent
    '''
    def __init__(self, client):
        self.client = client

    def notify(self, clipData, current=None):
        if clipData.URL in self.client.downloads:
            self.client.downloads.update({clipData.URL:clipData.status})

class Client(Ice.Application):
    ''' Ice application cliente  '''

    factory = None
    schedulers = {}
    schedulersURL = {}
    downloads = {}


    def get_topic_manager(self):
        '''
        Obtener el topic TopicManager
        '''
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

    def availableSchedulers(self):
        '''
        Returns the number of active schedulers in the factory
        '''
        return(self.factory.availableSchedulers())

    def connect(self,proxy):
        '''
        Connect to factory proxy
        '''
        proxy_factory = self.communicator().stringToProxy(proxy)
        self.factory = Downloader.SchedulerFactoryPrx.checkedCast(proxy_factory)
        if not self.factory:
            raise RuntimeError('Invalid proxy')

        topic_mgr = self.get_topic_manager()
        progress_topic = self.create_topic(topic_mgr, "ProgressTopic")
        adapter = self.communicator().createObjectAdapter("ProgressAdapter")
        servant_progress = ProgressEventI(self)
        subscriber_progress = adapter.addWithUUID(servant_progress)
        qos = {}
        progress_topic.subscribeAndGetPublisher(qos, subscriber_progress)
        adapter.activate()

    def connect_default(self):
        '''
        Connect to default factory proxy
        SchedulerFactory1 -t -e 1.1 @ DownloaderFactory.SchedulerFactoryAdapte
        '''
        proxy = 'SchedulerFactory1 -t -e 1.1 @ DownloaderFactory.SchedulerFactoryAdapter'
        proxy_factory = self.communicator().stringToProxy(proxy)
        self.factory = Downloader.SchedulerFactoryPrx.checkedCast(proxy_factory)
        if not self.factory:
            raise RuntimeError('Invalid proxy')
        topic_mgr = self.get_topic_manager()
        progress_topic = self.create_topic(topic_mgr, "ProgressTopic")
        adapter = self.communicator().createObjectAdapter("ProgressAdapter")
        servant_progress = ProgressEventI(self)
        subscriber_progress = adapter.addWithUUID(servant_progress)
        qos = {}
        progress_topic.subscribeAndGetPublisher(qos, subscriber_progress)
        adapter.activate()


    def show_progress(self):
        '''
        Shows the download process
        '''
        pprint.pprint(self.downloads)

    def getFile(self, song):
        '''
        Get the downloaded song and save it in the current directory
        '''
        key = random.choice(list(self.schedulers))
        song_list = self.schedulers[key].getSongList()
        if song in song_list:
            transfer = self.schedulers[key].get(song)
            destination = './{}'.format(song)
            self.receive(transfer, destination)
        else:
            print("Error")


    def receive(self, transfer, destination_file):
        '''
        Read a complete file using a Downloader.Transfer object
        '''
        with open(destination_file, 'wb') as file_contents:
            remoteEOF = False
            while not remoteEOF:
                data = transfer.recv(BLOCK_SIZE)
                # Remove additional byte added by str() at server
                if len(data) > 1:
                    data = data[1:]
                data = binascii.a2b_base64(data)
                remoteEOF = len(data) < BLOCK_SIZE
                if data:
                    file_contents.write(data)
            transfer.end()

    def create_schedule(self,name):
        '''
        Create a scheduler
        '''
        if name in self.schedulers:
            raise Downloader.SchedulerAlreadyExists
        schedule = self.factory.make(name)
        self.schedulers[name] = schedule

    def getSongList(self):
        '''
        Returns the list of songs
        '''
        if len(self.schedulers) is 0:
            print("No schedulers create")
        else:
            key = random.choice(list(self.schedulers))
            songs = self.schedulers[key].getSongList()
            return songs

    def cancel_task(self,line):
        ''' '''
        key = self.schedulersURL[line]
        self.schedulers[key].cancelTask(line)

    def killAll(self):
        '''
        Remove all the schedulers created by the client
        '''
        for schedule in self.schedulers:
            self.factory.kill(schedule)

    def kill(self,name):
        '''
        Remove a scheduler
        '''
        if name in self.schedulers:
            self.factory.kill(name)
            del(self.schedulers[name])
        else:
            raise Downloader.SchedulerNotFound


    def add_download(self,line):
        '''
        Add a download to a random scheduler
        '''
        if len(self.schedulers) is 0:
            print("No schedulers create")
        else:
            key = random.choice(list(self.schedulers))
            self.downloads[line] = None
            self.schedulers[key].begin_addDownloadTask(line)
            self.schedulersURL[line] = key
            print("Download add to the schedule {}".format(key))

    def run(self, argv):
        Shell(self).cmdloop()
        return 0


if __name__ == '__main__':
    APP = Client()
    sys.exit(APP.main(sys.argv))

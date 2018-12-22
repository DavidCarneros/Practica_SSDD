#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('downloader.ice')
import Downloader


class Client(Ice.Application):

    def run(self, argv):
        proxy = self.communicator().stringToProxy("SchedulerFactory1 -t -e 1.1:tcp -h 192.168.1.148 -p 10000 -t 60000:tcp -h 10.0.2.128 -p 10000 -t 60000")
        factory = Downloader.SchedulerFactoryPrx.checkedCast(proxy)

        if not factory:
            raise RuntimeError('Invalid proxy')

        schedule1 = factory.make("schedule1")

        print(schedule1.addDownloadTask("https://www.youtube.com/watch?v=lAg6IZc_uuU"))
        print(schedule1.addDownloadTask("https://www.youtube.com/watch?v=ppbhxukCd-4"))
        print(schedule1.getSongList())
        return 0


sys.exit(Client().main(sys.argv))

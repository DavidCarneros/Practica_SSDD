#!/usr/bin/python3
# -*- coding: utf-8 -*-
"usage: {} <server> <value>"

import sys

import Ice
Ice.loadSlice('Downloader.ice')
import DownloaderSlice


class Client(Ice.Application):

    def run(self, argv):
        base = self.communicator().stringToProxy(argv[1])
        downloader_server =  DownloaderSlice.DownloaderPrx.checkedCast(base)

        if not downloader_server:
            raise RuntimeError("Invalid proxy")

        print(downloader_server.download(argv[2]))

        print(downloader_server.getSongsList())

        return 0


if len(sys.argv) != 3:
    print(__doc__.format(__file__))
    sys.exit(1)


app = Client()
sys.exit(app.main(sys.argv))

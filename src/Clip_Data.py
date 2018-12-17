#/usr/bin/python3

import sys
import Ice
import IceStorm
#pylint: disable = E0401
#pyliny: disable = C0413
Ice.loadSlice("Downloader.ice")
import DownloaderSlice
from enum import Enum

class Status(Enum):
    Pending = 0
    InProgress = 1
    Done = 2
    Error = 3

class ClipData(Ice.Object):
    def __init__(self,URL='',clipName='',endpointTCP='',status=Status.Pending):
        self.URL = URL
        self.clipName = clipName
        self.endpointTCP = endpointTCP
        self.status = status

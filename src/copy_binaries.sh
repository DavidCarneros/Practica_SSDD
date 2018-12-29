#!/bin/bash

if [ -d /tmp/Downloader ];
then
  rm -r /tmp/Downloader
fi

mkdir /tmp/Downloader

cp Factory.py /tmp/Downloader
cp downloads_scheduler.py /tmp/Downloader
cp work_queue.py /tmp/Downloader
cp youtubedl.py /tmp/Downloader
cp downloader.ice /tmp/Downloader
cp SyncTimer.py /tmp/Downloader
cp Monitor.py /tmp/Downloader

icepatch2calc /tmp/Downloader

echo "Binarios copiados"

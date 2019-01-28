#!/bin/bash

if [ -d /tmp/db/node2 ];
then
  rm -r /tmp/db/node2
fi

mkdir /tmp/db/node2

echo "icegridnode --Ice.Config=node2.config"
icegridnode --Ice.Config=node2.config

#!/bin/bash

if [ -d /tmp/db ];
then
  rm -r /tmp/db
fi

mkdir /tmp/db
mkdir /tmp/db/node1
mkdir /tmp/db/registry

if [ -d /tmp/dl ];
then
  rm -r /tmp/dl
fi

mkdir /tmp/dl

echo "icegridnode --Ice.Config=node1.config"
icegridnode --Ice.Config=node1.config

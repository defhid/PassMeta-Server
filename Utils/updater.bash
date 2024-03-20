#!/bin/bash

# get and unzip
wget -P /tmp https://github.com/vlad120/PassMeta-Server/archive/refs/heads/master.zip
unzip /tmp/master.zip -d /tmp
rm /tmp/master.zip

# clear old (TODO: update root)
rm -f -r {dir}/App

# stop the service
docker compose stop fastapi

# copy and remove tmp
cp -a /tmp/PassMeta-Server-master/. {dir}
rm -r /tmp/PassMeta-Server-master

# rebuild container
docker compose create fastapi --force-recreate --build

# ask for the service start
printf "Start service now? (Y/n) \n"
read answ

if [ "$answ" == "Y" ];
then
    docker compose start fastapi
fi
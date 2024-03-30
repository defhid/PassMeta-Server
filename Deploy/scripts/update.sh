#!/bin/bash

# This file must be placed outside the root directory of the project, next to "passmeta"
#

cd "$(dirname "$0")" || exit 1

# prepare temp directories
test -e ./passmeta-tmp && rm -r ./passmeta-tmp
test -e ./passmeta-new && rm -r ./passmeta-new

# get and unzip
wget -P ./passmeta-tmp https://github.com/vlad120/PassMeta-Server/archive/refs/heads/master.zip || exit 1
unzip ./passmeta-tmp/master.zip -d ./passmeta-tmp || exit 1

# prepare files
mkdir ./passmeta-new || exit 1
cp -a ./passmeta-tmp/PassMeta-Server-master/App ./passmeta-new/App || exit 1
cp -a ./passmeta-tmp/PassMeta-Server-master/Deploy ./passmeta-new/Deploy || exit 1
cp ./passmeta-tmp/PassMeta-Server-master/main.py ./passmeta-new/main.py || exit 1
cp ./passmeta-tmp/PassMeta-Server-master/requirements.txt ./passmeta-new/requirements.txt || exit 1
cp ./passmeta-tmp/PassMeta-Server-master/Dockerfile ./passmeta-new/Dockerfile || exit 1
cp ./passmeta/Deploy/.env.local ./passmeta-new/Deploy/.env.local
rm -r ./passmeta-tmp

# stop services
bash ./passmeta/Deploy/scripts/stop.sh || exit 1

# swap new & current & old directories
rm -f -r ./passmeta-old
mv ./passmeta ./passmeta-old || exit 1
mv ./passmeta-new ./passmeta || exit 1

# rebuild & start container
bash ./passmeta/Deploy/scripts/rebuild.sh || exit 1
echo "----"
echo "Successfully updated!"
read -p "Start services now? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
bash ./passmeta/Deploy/scripts/start.sh
fi

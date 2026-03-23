#!/bin/sh
cd /tmp 

if ! [  -f "/tmp/tox.tar.gz.enc" ]; then
    wget https://github.com/definitly486/definitly486/releases/download/tox/tox.tar.gz.enc 
fi


openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -e -d -in  tox.tar.gz.enc  -out tox.tar.gz
tar -xJf tox.tar.gz
rm -R $HOME/.config/tox
cp -R tox  $HOME/.config
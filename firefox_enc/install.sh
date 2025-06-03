#!/bin/sh
cd /tmp 

if ! [  -f "/tmp/firefox.tar.xz.enc" ]; then
    wget https://github.com/definitly486/definitly486/releases/download/firefox.enc/firefox.tar.xz.enc
fi


openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -e -d -in  firefox.tar.xz.enc  -out firefox.tar.xz
tar -xJf firefox.tar.xz
rm -R $HOME/.mozilla
mkdir $HOME/.mozilla
cp -R firefox  $HOME/.mozilla
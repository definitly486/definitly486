#!/bin/sh
cd /tmp 

if ! [  -f "/tmp/pale.moon.tar.xz.enc" ]; then
    wget https://github.com/definitly486/definitly486/releases/download/palemoon.enc/pale.moon.tar.xz.enc
fi


openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -e -d -in  pale.moon.tar.xz.enc  -out pale.moon.tar.xz
tar -xJf pale.moon.tar.xz
rm -R $HOME/".moonchild productions"
mkdir $HOME/".moonchild productions"
cp -R "pale moon"  $HOME/".moonchild productions"
#!/bin/sh

sudo apt-get install -y  zlib1g-dev libffi-dev

NAME=Python-3.9.0b4
VER=$(echo $NAME | sed 's/.......//' |  sed 's/^\(.*\).$/\1/' | sed 's/^\(.*\).$/\1/')
wget https://www.python.org/ftp/python/$VER/$NAME.tar.xz
tar xf $NAME.tar.xz
cd $NAME
./configure
make && sudo make install


sudo ln -s $HOME/.local/bin/yt-dlp /usr/bin/yt-dlp

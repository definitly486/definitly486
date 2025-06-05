#!/bin/sh

sudo apt-get install -y  zlib1g-dev libffi-dev

NAME=Python-3.9.0b4
VER=$(echo $NAME | sed 's/.......//' |  sed 's/^\(.*\).$/\1/' | sed 's/^\(.*\).$/\1/')
wget https://www.python.org/ftp/python/$VER/$NAME.tar.xz
tar xf $NAME.tar.xz

cp Setup $NAME/Modules
sudo rm sudo rm /usr/local/bin/openssl

cd $NAME
./configure
make && sudo make install


sudo ln -s $HOME/.local/bin/yt-dlp /usr/bin/yt-dlp
sudo ln -s  $HOME/.local/bin/streamlink /usr/bin/streamlink

pip3  install pipx
$HOME/.local/bin/pipx install git+https://github.com/streamlink/streamlink.git
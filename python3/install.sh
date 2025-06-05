#!/bin/sh

sudo apt-get install -y  zlib1g-dev libffi-dev realpath

DIR=$(dirname "$(realpath $0)")


NAME=Python-3.8.13
VER=$(echo $NAME | sed 's/.......//')
wget -P $DIR  https://www.python.org/ftp/python/$VER/$NAME.tar.xz 
tar xf $DIR/$NAME.tar.xz

cp $DIR/Setup $DIR/$NAME/Modules
 sudo rm /usr/local/bin/openssl

cd $DIR/$NAME
./configure
make && sudo make install


sudo ln -s $HOME/.local/bin/yt-dlp /usr/bin/yt-dlp
sudo ln -s  $HOME/.local/bin/streamlink /usr/bin/streamlink

pip3  install pipx
$HOME/.local/bin/pipx install git+https://github.com/streamlink/streamlink.git
$HOME/.local/bin/pipx install yt-dlp
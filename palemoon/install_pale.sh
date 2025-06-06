cd /tmp

NAME=palemoon-31.4.2.linux-x86_64-gtk2.tar.xz

if ! [  -f "/tmp/$NAME" ]; then
     wget https://archive.palemoon.org/palemoon/31.x/31.4.2/$NAME
fi

tar -xf $NAME -C $HOME
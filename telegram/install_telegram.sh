#!/bin/sh

cd /tmp

if ! [  -f "/tmp/tsetup.5.15.2.tar.xz" ]; then
     wget http://telegram.org/dl/desktop/linux/tsetup.5.15.2.tar.xz
fi

tar -xf tsetup.5.15.2.tar.xz -C $HOME

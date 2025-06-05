#!/bin/sh

ver=139.0.1

cd /tmp

if ! [  -f "/tmp/firefox-$ver.tar.xz" ]; then
     wget https://ftp.mozilla.org/pub/firefox/releases/139.0.1/linux-x86_64/ru/firefox-$ver.tar.xz
fi

tar -xf firefox-$ver.tar.xz -C $HOME
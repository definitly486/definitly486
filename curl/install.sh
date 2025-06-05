#!/bin/sh

sudo apt-get autoconf2.13 libtool

git clone --depth=1  https://github.com/curl/curl

cd curl

autoreconf -fi
./configure --with-openssl --without-libpsl
make && sudo make install 
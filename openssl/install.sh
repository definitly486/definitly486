#!/bin/sh

wget https://github.com/openssl/openssl/releases/download/OpenSSL_1_1_1w/openssl-1.1.1w.tar.gz
tar xf openssl-1.1.1w.tar.gz

cd openssl-1.1.1w
./config
make && sudo make install

sudo cp /usr/local/lib/libssl.so.1.1 /usr/lib
sudo cp /usr/local/lib/libcrypto.so.1.1  /usr/lib
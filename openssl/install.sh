#!/bin/sh

wget https://github.com/openssl/openssl/releases/download/OpenSSL_1_1_1w/openssl-1.1.1w.tar.gz
tar xf openssl-1.1.1w.tar.gz

cd openssl-1.1.1w



sudo cp /usr/local/lib64/libcrypto.so.1.1 /usr/lib
sudo cp /usr/local/lib64/libssl.so.1.1 /usr/lib
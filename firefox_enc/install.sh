#!/bin/sh

wget https://github.com/definitly486/definitly486/releases/download/firefox.enc/firefox.tar.xz.enc
openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -e -d -in  firefox.tar.xz.enc  -out firefox.tar.xz
tar -xJf firefox.tar.xz
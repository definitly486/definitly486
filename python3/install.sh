#!/bin/sh

NAME=Python-3.9.0b4

wget https://www.python.org/ftp/python/3.11.0/$NAME.tar.xz
tar xf $NAME.tar.xz
cd $NAME
./configure

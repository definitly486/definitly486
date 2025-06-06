#!/bin/sh
wget   --no-check-certificate   https://sources.voidlinux.org/sshpass-1.10/sshpass-1.10.tar.gz
tar -xf sshpass-1.10.tar.gz
cd sshpass-1.10
./configure
sudo make install
sudo cp /usr/local/bin/sshpass /usr/bin
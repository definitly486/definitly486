#!/bin/sh
cd /tmp 

if ! [  -f "/tmp/TelegramDesktop.tar.xz.enc" ]; then
      wget https://github.com/definitly486/definitly486/releases/download/telegramdesktop/TelegramDesktop.tar.xz.enc
fi

openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -e -d -in TelegramDesktop.tar.xz.enc -out TelegramDesktop.tar.xz
rm -R $HOME/.local/share/TelegramDesktop/tdata
tar -xJf TelegramDesktop.tar.xz
cp -R TelegramDesktop/tdata  $HOME/.local/share/TelegramDesktop/

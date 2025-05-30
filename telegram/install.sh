#!/bin/sh

wget https://github.com/definitly486/definitly486/releases/download/telegramdesktop/TelegramDesktop.tar.xz.enc
openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -e -d -in TelegramDesktop.tar.xz.enc -out TelegramDesktop.tar.xz
tar -xJf TelegramDesktop.tar.xz
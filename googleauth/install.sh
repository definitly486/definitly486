#!/bin/sh
DIR=$(dirname "$(realpath $0)")

cd /tmp 

if ! [  -f "/tmp/authenticator.txt.enc" ]; then
    wget https://github.com/definitly486/definitly486/releases/download/googleauth/authenticator.txt.enc
fi


openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -e -d -in  authenticator.txt.enc  -out $DIR/authenticator.txt

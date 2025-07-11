#!/bin/sh
termux-setup-storage
DIR=$(dirname "$(realpath $0)")

cd $HOME
curl -L -o $TERMUX__PREFIX/tmp/main.tar.gz https://github.com/definitly486/Lenovo_Tab_3_7_TB3-730X/archive/main.tar.gz
tar -xf $TERMUX__PREFIX/tmp/main.tar.gz -C $HOME
adb shell pm grant com.conena.navigation.gesture.control android.permission.WRITE_SECURE_SETTINGS 

https://raw.githubusercontent.com/Syavar/V2ray-Configs/refs/heads/main/OK_TLS_telegram.org_base64.txt

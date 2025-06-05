#!/bin/sh

ver=139.0.1

cd /tmp

if ! [  -f "/tmp/firefox-$ver.tar.xz" ]; then
     wget https://ftp.mozilla.org/pub/firefox/releases/139.0.1/linux-x86_64/ru/firefox-$ver.tar.xz
fi

tar -xf firefox-$ver.tar.xz -C $HOME


fix () {

cat << EOF >   stub.c
#include <stdio.h>
void gdk_window_show_window_menu(void) {}
EOF

cc -shared -o stub.so stub.c -fPIC


cat << EOF >   firefox_run.sh
LD_PRELOAD=./stub.so ./firefox "\$@"
EOF

chmod +x firerox_run.sh
}



if [ "14.04" = "$(cat /etc/os-release | grep  VERSION_ID | grep -oP '(?<=").+?(?=")')"  ]   ; then
    
    cd $HOME/firefox
    echo "apply fix"
    fix 
else
   exit 
fi
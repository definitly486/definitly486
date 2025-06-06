cd /tmp

if ! [  -f "/tmp/palemoon-33.7.1.linux-x86_64-gtk2.tar.xz" ]; then
     wget https://archive.palemoon.org/palemoon/33.x/33.7.1/Linux/palemoon-33.7.1.linux-x86_64-gtk2.tar.xz
fi

tar -xf palemoon-33.7.1.linux-x86_64-gtk2.tar.xz -C $HOME
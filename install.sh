#!/bin/sh

if test "$(id -u)" -ne 0; then
	printf "%s must be run as root\n" "${0##*/}"
	exit 1
fi



install_apt () {

 apt install git mc screen htop sshpass 

}

install_dnf  () {

 dnf  install git mc screen htop sshpass openssl 

}

if [ "debian" = "$(uname -n)"   ] ; then
    echo "install packages for debian "
    install_apt
elif [ "debian_version" = "$(ls /etc | grep debian)"   ] ; then
    echo "install packages for debian "
    install_apt
else
    echo "install packages for fedora"
    install_dnf
fi

#sudo apt-get install build-essential libmnl-dev libcap-dev zlib1g-dev  libsystemd-dev

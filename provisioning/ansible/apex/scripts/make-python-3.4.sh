#!/usr/bin/env bash

if [ ! -f /usr/local/bin/easy_install-3.4 ]; then
    cd ~
    wget https://www.python.org/ftp/python/3.4.1/Python-3.4.1.tar.xz
    tar xf Python-3.4.1.tar.xz
    cd Python-3.4.1
    ./configure
    make
    make install
    ln -s /usr/local/bin/easy_install-3.4 /usr/bin/easy_install-3.4
fi


#rm /usr/bin/python
#ln -s python3.4 /usr/bin/python
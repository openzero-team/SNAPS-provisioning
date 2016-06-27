#!/usr/bin/env bash

cd ~/rift

git checkout tags/v0.0 -b v0.0
./rift-shell
make rw.ext
make -j1 rw
make rw.start_lp
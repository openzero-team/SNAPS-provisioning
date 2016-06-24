#!/usr/bin/env bash

# Read in properties
. /etc/default/lxc-net

echo "    apt-http-proxy: http://$LXC_ADDR:8000" >> ~/.juju/environments.yaml
echo "    apt-https-proxy: http://$LXC_ADDR:8000\n" >> ~/.juju/environments.yaml
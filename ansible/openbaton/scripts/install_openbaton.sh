#!/usr/bin/env bash

echo '{{ rabbit_broker_ip }}\n{{ rabbit_mgmt_port }}\n{{ rabbit_enable_security }}\n{{ rabbit_enable_https }}\n' | \
bash <(curl -fsSkL http://get.openbaton.org/bootstrap) | \
tee /tmp/install_openbaton.out

cd /opt/openbaton/nfvo/

./openbaton.sh start

#!/usr/bin/env bash

wget -O /tmp/install-openmano.sh "https://osm.etsi.org/gitweb/?p=osm/openmano.git;a=blob_plain;f=scripts/install-openmano.sh"

chmod +x /tmp/install-openmano.sh

/tmp/install-openmano.sh -u root -p cable123 -q | tee /tmp/install-openmano.out

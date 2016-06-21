#!/usr/bin/env bash

wget -O install-openmano.sh "https://osm.etsi.org/gitweb/?p=osm/openmano.git;a=blob_plain;f=scripts/install-openmano.sh"

chmod +x install-openmano.sh

./install-openmano.sh

#!/usr/bin/env bash

~/bin/service-openmano start

~/bin/openmano tenant-create {{ tenant_name }}
#tenant_info=( $(~/bin/openmano tenant-list) )
#export OPENMANO_TENANT=$tenant_info[0]
# TODO - determine if the name is sufficient or whether or not we need to extract the tenant ID and use that instead
export OPENMANO_TENANT={{ tenant_name }}
echo "export OPENMANO_TENANT=$OPENMANO_TENANT" >> ~/.bashrc

export OPENMANO_HOST=0.0.0.0
echo "export OPENMANO_HOST=$OPENMANO_HOST" >> ~/.bashrc

# Configure
~/bin/openmano datacenter-create --type openstack --description "OpenStack Datacenter" {{ datacenter_name }} {{ os_auth_url }}
#datacenter_info=( $(~/bin/openmano datacenter-list) )
#export OPENMANO_DATACENTER=$datacenter_info[0]
# TODO - determine if the name is sufficient or whether or not we need to extract the datacenter ID and use that instead
export OPENMANO_DATACENTER={{ datacenter_name }}
echo "export OPENMANO_DATACENTER=$OPENMANO_DATACENTER" >> ~/.bashrc

~/bin/openmano datacenter-attach openstack-site --user={{ os_user }} --password={{ os_pass }} --vim-tenant-name={{ os_tenant }}
~/bin/openmano datacenter-netmap-upload -f --datacenter openstack-site

# Sample adding example VNFs to orchestrator
~/bin/openmano vnf-create ~/openmano/vnfs/examples/dataplaneVNF1.yaml
~/bin/openmano vnf-create ~/openmano/vnfs/examples/dataplaneVNF2.yaml

# Sample create scenarios - currently error with "unknown 'VNF model' linux at 'topology':'nodes':'linux1'"
#~/bin/openmano scenario-create ~/openmano/scenarios/examples/simple.yaml
#~/bin/openmano scenario-create ~/openmano/scenarios/examples/complex.yaml

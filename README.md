# Python scripts for creating virtual environments on OpenStack with Ansible playbooks for provisioning.

## Runtime Environment Setup
  * Python 2.7 (recommend leveraging a Virtual Python runtime)
    * OpenStack clients 2.0.0
      * glance (python-glanceclient)
      * neutron (python-neutronclient)
      * keystone (python-keystoneclient)
      * nova (python-novaclient)
    * scp
    * ansible (1.9.4) - soon to be 2.0.0
      * Crypto (installed by ansible)
  * set PYTHONPATH
    * cd <path to repo>/python
    * export PYTHONPATH=$PYTHONPATH:$(pwd)

## [Host SSH settings (until Ansible 2.0 upgrade has been completed)](doc/HostSSHConfig.md)
## [Unit Testing](doc/UnitTesting.md)
## [Virtual Environment Deployment](doc/VirtEnvDeploy.md)

Also see the [CableLabs project wiki page](https://community.cablelabs.com/wiki/display/SNAPS/OpenStack+Instantiation%2C+Provisioning%2C+and+Testing)
for more information on these scripts.

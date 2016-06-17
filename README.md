# Python scripts for creating virtual environments on OpenStack with Ansible playbooks for provisioning.

## Runtime Environment Setup
  * Python 2.7 (recommend leveraging a Virtual Python runtime)
    * OpenStack clients
      * python-glanceclient - tested with 2.0.0
      * python-neutronclient - tested with 4.2.0
      * python-keystoneclient - tested with 3.1.0
      * python-novaclient - tested with 4.0.0
    * scp - tested with 0.10.2
    * ansible 2.1.0
      * cryptography 1.4 (installed by ansible)
      * pycrypto 2.6.1 (installed by ansible)
  * set PYTHONPATH
    * cd <path to repo>/python
    * export PYTHONPATH=$PYTHONPATH:$(pwd)

## [Host SSH settings (required for clouds running behind a proxy)](doc/HostSSHConfig.md)
### (note: Ansible 2.x should allow for the ProxyCommand to be set programatically but is currently not working.)
## [Unit Testing](doc/UnitTesting.md)
## [Virtual Environment Deployment](doc/VirtEnvDeploy.md)

Also see the [CableLabs project wiki page](https://community.cablelabs.com/wiki/display/SNAPS/OpenStack+Instantiation%2C+Provisioning%2C+and+Testing)
for more information on these scripts.

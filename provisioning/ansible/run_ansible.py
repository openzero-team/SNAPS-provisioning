#!/usr/bin/python
#
# This script is responsible for executing an Ansible task.
# Equivalent to cmdline call
# sudo ansible -i provisioning/ansible/conf/inventory -m ping -u root all -k
# TODO - Make configurable. This cut was checked in simply to demonstrate how it is done.
import logging

from ansible.runner import Runner
from ansible.inventory import Inventory

logger = logging.getLogger('run_playbook')


def main():
    logging.basicConfig(level=logging.DEBUG)
    logger.info('Start Run Ansible')

    hosts = ['10.197.123.211']
    inventory = Inventory(host_list=hosts)

    """
    NOTE: This test and any others that call ansible will most likely fail unless you do one of
    two things:
    1. Have a ~/.ansible.cfg (or alternate means) to set host_key_checking = False
    2. Set the following environment variable in your executing shell: ANSIBLE_HOST_KEY_CHECKING=False
    Should this not be performed, the creation of the host ssh key will cause your ansible calls to fail.
    """
    runner = Runner(module_name='ping', inventory=inventory, pattern='all', remote_user='centos',
                    private_key_file='/tmp/testKP')
    data = runner.run()
    print data


if __name__ == '__main__':
    main()

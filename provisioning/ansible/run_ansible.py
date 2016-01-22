#!/usr/bin/python
#
# This script is responsible for executing an Ansible playbook.
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

    hosts = ['192.168.253.142']
    inventory = Inventory(host_list=hosts)

    runner = Runner(module_name='ping', inventory=inventory, pattern='all', remote_user='root', remote_pass='cable123')
    data = runner.run()
    print data


if __name__ == '__main__':
    main()

#!/usr/bin/python
#
# This script is responsible for executing the Ansible playbook java7.yaml
# Equivalent to cmdline call
# ansible-playbook -i conf/inventory ansible/playbooks/java7.yaml -u {sudo user} -U root --private-key {path}
# TODO - Make configurable. This cut was checked in simply to demonstrate how it is done.

import logging

from ansible.playbook import PlayBook
from ansible.inventory import Inventory
from ansible.callbacks import AggregateStats
from ansible.callbacks import PlaybookRunnerCallbacks
from ansible.callbacks import PlaybookCallbacks
from ansible import utils

logger = logging.getLogger('OpenVSwitch')


def main():
    logging.basicConfig(level=logging.DEBUG)
    logger.info('Start Run Ansible')

    hosts = ['10.197.123.207']
    inventory = Inventory(host_list=hosts)

    stats = AggregateStats()
    run_cb = PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
    pb_cb = PlaybookCallbacks(verbose=utils.VERBOSITY)

    runner = PlayBook(playbook='provisioning/ansible/openvswitch/main.yml', inventory=inventory, remote_user='centos',
                      sudo_user='root', private_key_file='/tmp/unimgr', sudo=True, callbacks=pb_cb,
                      runner_callbacks=run_cb, stats=stats)
    data = runner.run()
    print data


if __name__ == '__main__':
    main()

#!/usr/bin/python
#
# This script is responsible for executing an Ansible playbook
# Equivalent to cmdline call
# ansible-playbook -i conf/inventory ansible/playbooks/java8.yaml -u root -k
# TODO - Make configurable. This cut was checked in simply to demonstrate how it is done.

import logging

from ansible.playbook import PlayBook
from ansible.inventory import Inventory
from ansible.callbacks import AggregateStats
from ansible.callbacks import PlaybookRunnerCallbacks
from ansible.callbacks import PlaybookCallbacks
from ansible import utils

logger = logging.getLogger('run_ansible-playbook')


def main():
    logging.basicConfig(level=logging.DEBUG)
    logger.info('Start Run Ansible')

    hosts = ['192.168.253.142']
    inventory = Inventory(host_list=hosts)

    stats = AggregateStats()
    run_cb = PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
    pb_cb = PlaybookCallbacks(verbose=utils.VERBOSITY)

    runner = PlayBook(playbook='playbooks/java8.yaml', inventory=inventory, remote_user='root', remote_pass='cable123',
                      stats=stats, callbacks=pb_cb, runner_callbacks=run_cb)
    data = runner.run()
    print data


if __name__ == '__main__':
    main()

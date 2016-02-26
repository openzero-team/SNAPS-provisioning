#!/usr/bin/python
#
# This script is responsible for executing an Ansible playbook.
# Equivalent to cmdline call
# sudo ansible-playbook -i provisioning/ansible/conf/inventory openvswitch/main.yml
# TODO - Make configurable. This cut was checked in simply to demonstrate how it is done.
import logging

from ansible.playbook import PlayBook
from ansible.callbacks import AggregateStats
from ansible.callbacks import PlaybookRunnerCallbacks
from ansible.callbacks import PlaybookCallbacks
from ansible import utils

logger = logging.getLogger('run_playbook')


def main():
    logging.basicConfig(level=logging.DEBUG)
    logger.info('Start Run Ansible')

    hosts = ['10.197.123.202', '10.197.123.204']

    """
    NOTE: This test and any others that call ansible will most likely fail unless you do one of
    two things:
    1. Have a ~/.ansible.cfg (or alternate means) to set host_key_checking = False
    2. Set the following environment variable in your executing shell: ANSIBLE_HOST_KEY_CHECKING=False
    Should this not be performed, the creation of the host ssh key will cause your ansible calls to fail.
    """
    stats = AggregateStats()
    run_cb = PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
    pb_cb = PlaybookCallbacks(verbose=utils.VERBOSITY)

    # TODO - need to find a better means of finding this playbook.
    runner = PlayBook(playbook='openvswitch/main.yml',
                      host_list=hosts,
                      remote_user='centos',
                      private_key_file='/tmp/unimgr',
                      callbacks=pb_cb, runner_callbacks=run_cb, stats=stats)
    data = runner.run()
    print data


if __name__ == '__main__':
    main()

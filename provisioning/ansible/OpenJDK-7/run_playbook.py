#!/usr/bin/python
#
# Copyright (c) 2016 Cable Television Laboratories, Inc. ("CableLabs")
#                    and others.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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

logger = logging.getLogger('OpenJDK-7-Playbook')


def main():
    logging.basicConfig(level=logging.DEBUG)
    logger.info('Start Run Ansible')

    hosts = ['10.197.123.211']
    inventory = Inventory(host_list=hosts)

    stats = AggregateStats()
    run_cb = PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
    pb_cb = PlaybookCallbacks(verbose=utils.VERBOSITY)

    runner = PlayBook(playbook='playbooks/java7.yaml', inventory=inventory, remote_user='centos',
                      sudo_user='root', private_key_file='/tmp/testKP', sudo=True, callbacks=pb_cb,
                      runner_callbacks=run_cb, stats=stats)
    data = runner.run()
    print data


if __name__ == '__main__':
    main()

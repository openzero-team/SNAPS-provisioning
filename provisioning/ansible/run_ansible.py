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

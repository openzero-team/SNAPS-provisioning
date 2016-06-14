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
import logging

from collections import namedtuple

import re
import os
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.executor.playbook_executor import PlaybookExecutor

__author__ = 'spisarski'

logger = logging.getLogger('ansible_utils')


def apply_playbook(playbook_path, hosts_inv, host_user, ssh_priv_key_file_path, variables=None, proxy_setting=None):
    """
    Executes an Ansible playbook to the given host
    :param playbook_path: the (relative) path to the Ansible playbook
    :param hosts_inv: a list of hostnames/ip addresses to which to apply the Ansible playbook
    :param host_user: A user for the host instances (must be a password-less sudo user if playbook has "sudo: yes"
    :param ssh_priv_key_file_path: the file location of the ssh key
    :param variables: a dictionary containing any substitution variables needed by the Jinga 2 templates
    :param proxy_setting: string containing host:port of the proxy server in use
    :return: the results
    """
    if not os.path.isfile(playbook_path):
        raise Exception('Requested playbook not found - ' + playbook_path)
    if not os.path.isfile(ssh_priv_key_file_path):
        raise Exception('Requested private SSH key not found - ' + ssh_priv_key_file_path)

    import ansible.constants
    ansible.constants.HOST_KEY_CHECKING = False

    variable_manager = VariableManager()
    if variables:
        variable_manager.extra_vars = variables

    loader = DataLoader()
    inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=hosts_inv)
    variable_manager.set_inventory(inventory)
    loader = DataLoader()

    ssh_common_args = None
    ssh_extra_args = None
    ssh_connection = 'ssh'
    proxy_command = None
    if proxy_setting:
        tokens = re.split(':', proxy_setting)
        # TODO - Need to configure the proxy settings to avoid adding entries into the host's ~/.ssh/config file

    options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection', 'module_path',
                                     'forks', 'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args',
                                     'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user',
                                     'verbosity', 'check', 'host_key_checking', 'transport', 'proxy_command'])
    ansible_opts = options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection=ssh_connection,
                           module_path=None, forks=100, remote_user=host_user, private_key_file=ssh_priv_key_file_path,
                           ssh_common_args=ssh_common_args, ssh_extra_args=ssh_extra_args, sftp_extra_args=None,
                           scp_extra_args=None, become=None, become_method=None, become_user='root', verbosity=1111,
                           check=False, host_key_checking=True, transport='paramiko', proxy_command=proxy_command)
    logger.debug('Setting up Ansible Playbook Executor')
    executor = PlaybookExecutor(
        playbooks=[playbook_path],
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        options=ansible_opts,
        passwords=None)

    logger.debug('Executing Ansible Playbook - ' + playbook_path)
    retval = executor.run()

    if retval != 0:
        logger.error('Playbook application failed [' + playbook_path + '] with return value of - ' + str(retval))
        raise Exception('Playbook not applied - ' + playbook_path)

    return retval


def ssh_client(ip, user, private_key_filepath, proxy_settings=None):
    """
    Retrieves and attemts an SSH connection
    :param ip: the IP of the host to connect
    :param user: the user with which to connect
    :param private_key_filepath: the path to the private key file
    :param proxy_settings: optional proxy settings in the form <hostname|IP>:<port>
    :return: the SSH client if can connect else false
    """
    import paramiko

    logger.debug('Retrieving SSH client')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    proxy = None
    if proxy_settings:
        logger.debug('Setting up SSH proxy settings')
        tokens = re.split(':', proxy_settings)
        proxy = paramiko.ProxyCommand('../ansible/conf/ssh/corkscrew ' + tokens[0] + ' ' + tokens[1] + ' ' +
                                      ip + ' 22')
        logger.info('Attempting to connect to ' + ip)

    try:
        ssh.connect(ip, username=user, key_filename=private_key_filepath, sock=proxy)
        return ssh
    except Exception as e:
        logger.warn('Unable to connect via SSH with message - ' + e.message)

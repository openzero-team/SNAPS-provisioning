#!/usr/bin/python
#
# This script is responsible for executing the Ansible playbook java7.yaml
# Equivalent to cmdline call
# ansible-playbook -i conf/inventory ansible/playbooks/java7.yaml -u {sudo user} -U root --private-key {path}
# TODO - Make configurable. This cut was checked in simply to demonstrate how it is done.

import logging
from tempfile import NamedTemporaryFile

from ansible.playbook import PlayBook
from ansible.callbacks import AggregateStats
from ansible.callbacks import PlaybookRunnerCallbacks
from ansible.callbacks import PlaybookCallbacks
from ansible import utils
import jinja2

logger = logging.getLogger('centos-network-setup')


def main():
    logging.basicConfig(level=logging.DEBUG)
    logger.info('Start Run Ansible')

    inventory = """
    [this]
    {{ floating_ip }}

    [this:vars]
    nic_name={{nic_name}}
    nic_ip={{nic_ip}}
    """

    inventory_template = jinja2.Template(inventory)
    rendered_inventory = inventory_template.render({
        'floating_ip': '10.197.123.213',
        'nic_name': 'eth1',
        'nic_ip': '10.1.1.5'
    })

    hosts = NamedTemporaryFile(delete=False)
    hosts.write(rendered_inventory)
    hosts.close()

    stats = AggregateStats()
    run_cb = PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
    pb_cb = PlaybookCallbacks(verbose=utils.VERBOSITY)

    runner = PlayBook(playbook='playbooks/configure_host.yml', host_list=hosts.name,
                      remote_user='centos',
                      sudo_user='root', private_key_file='/tmp/testKP1', sudo=True, callbacks=pb_cb,
                      runner_callbacks=run_cb, stats=stats)
    data = runner.run()
    print data


if __name__ == '__main__':
    main()

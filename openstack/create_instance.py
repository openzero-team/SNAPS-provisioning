import time
import logging

import nova_utils

logger = logging.getLogger('create_instance')


class OpenStackVmInstance:
    """
    Class responsible for creating a VM instance in OpenStack
    """

    def __init__(self, os_creds, name, flavor, image, ports, keypair_name=None, floating_ip_conf=None, userdata=None):
        """
        Constructor
        :param os_creds: The connection credentials to the OpenStack API
        :param name: The name of the OpenStack instance to be deployed
        :param flavor: The size of the VM to be deployed (i.e. 'm1.small')
        :param image: The OpenStack image on which to deploy the VM
        :param ports: List of ports (NICs) to deploy to the VM
        :param keypair_name: The name of the keypair (Optional)
        :param floating_ip_conf: The configuration for the addition of a floating IP to an instance (Optional)
        :param userdata: The post installation script as a string or a file object (Optional)
        :raises Exception
        """
        self.name = name
        self.image = image
        self.ports = ports
        self.keypair_name = keypair_name
        self.floating_ip_conf = floating_ip_conf
        self.floating_ip = None
        self.userdata = userdata
        self.vm = None
        self.nova = nova_utils.nova_client(os_creds)

        # Validate that the flavor is supported
        self.flavor = self.nova.flavors.find(name=flavor)
        if not self.flavor:
            raise Exception

    def create(self):
        """
        Creates a VM instance
        :return: The VM reference object
        """
        # TODO - need to query instances and not deploy if one exists
        servers = self.nova.servers.list()
        for server in servers:
            if server.name == self.name:
                self.vm = server
                logger.info('Found existing machine with name - ' + self.name)
                return self.vm

        nics = []
        for port in self.ports:
            kv = dict()
            kv['port-id'] = port['port']['id']
            nics.append(kv)

        logger.info('Creating VM with name - ' + self.name)
        self.vm = self.nova.servers.create(
            name=self.name,
            flavor=self.flavor,
            image=self.image,
            nics=nics,
            key_name=self.keypair_name,
            userdata=self.userdata)
        logger.info('Created instance with name - ' + self.name)

        if self.floating_ip_conf:
            for port in self.ports:
                if port['port']['name'] == self.floating_ip_conf['port_name']:
                    self.floating_ip = nova_utils.create_floating_ip(self.nova, self.floating_ip_conf['ext_net'])
                    logger.info('Created floating IP ' + self.floating_ip.ip)
                    # TODO - Remove sleep below. Currently only works when waiting a bit after floating IP creation
                    time.sleep(5)
                    try:
                        self.vm.add_floating_ip(self.floating_ip, port['port']['dns_assignment'][0]['ip_address'])
                        logger.info('Added floating IP to port ' + port['port']['name'])
                    except:
                        logger.error('Error adding floating IP to instance')
                        pass

        return self.vm

    def clean(self):
        """
        Destroys the VM instance
        """
        if self.vm:
            self.nova.servers.delete(self.vm)

        if self.floating_ip:
            nova_utils.delete_floating_ip(self.nova, self.floating_ip)

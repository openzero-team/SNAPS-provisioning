import logging
import neutron_utils

logger = logging.getLogger('NeutronNetwork')


class CreateNetwork:
    """
    Class responsible for creating a network in OpenStack

    All tasks have been designed after the vPing scenario in the OPNFV functest repository. We will want to make
    this class more flexible, expand it beyond the private network. Additionally, many of the private methods here
    should probably make their way into a file named something like neutron_utils.py.
    """

    def __init__(self, username, password, os_auth_url, tenant_name, priv_net_name, priv_subnet_name, priv_subnet_cidr,
                 router_name):
        """Constructor"""
        self.username = username
        self.password = password
        self.os_auth_url = os_auth_url
        self.tenant_name = tenant_name
        self.priv_net_name = priv_net_name
        self.priv_subnet_name = priv_subnet_name
        self.priv_subnet_cidr = priv_subnet_cidr
        self.router_name = router_name
        self.neutron = neutron_utils.neutron_client(self.username, self.password, self.os_auth_url, self.tenant_name)
        self.neutron.format = 'json'
        self.network = None
        self.subnet = None
        self.router = None
        self.interface_router = None

    def create(self):
        """
        Responsible for creating not only the network but then a private subnet, router, and an interface to the router.
        """
        logger.info('Creating neutron network %s...' % self.priv_net_name)
        self.network = neutron_utils.create_network(self.neutron, self.priv_net_name)
        logger.debug("Network '%s' created successfully" % self.network['network']['id'])
        logger.debug('Creating Subnet....')
        self.subnet = neutron_utils.create_subnet(self.neutron, self.network, self.priv_subnet_name,
                                                          self.priv_subnet_cidr)

        logger.debug("Subnet '%s' created successfully" % self.subnet['subnets'][0]['id'])
        logger.debug('Creating Router...')
        self.router = neutron_utils.create_router(self.neutron, self.router_name)

        logger.debug("Router '%s' created successfully" % self.router['router']['id'])
        logger.debug('Adding router to subnet...')

        self.interface_router = neutron_utils.add_interface_router(self.neutron, self.router, self.subnet)

        if not self.interface_router:
            raise Exception

    def clean(self):
        """
        Removes and deletes all items created in reverse order.
        """
        neutron_utils.remove_interface_router(self.neutron, self.router, self.subnet)
        neutron_utils.delete_router(self.neutron, self.router)
        neutron_utils.delete_subnet(self.neutron, self.subnet)
        neutron_utils.delete_network(self.neutron, self.network)

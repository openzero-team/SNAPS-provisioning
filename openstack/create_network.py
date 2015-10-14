import logging
import neutron_utils
from neutronclient.v2_0 import client as neutronclient

logger = logging.getLogger('NeutronNetwork')


class CreateNetwork:
    """
    Class responsible for creating a network in OpenStack

    All tasks have been designed after the vPing scenario in the OPNFV functest repository. We will want to make
    this class more flexible, expand it beyond the private network. Additionally, many of the private methods here
    should probably make their way into a file named something like neutron_utils.py.
    """

    def __init__(self, username, password, osAuthUrl, tenantName, privNetName, privSubName, privSubCidr, routerName):
        """Constructor"""
        self.username = username
        self.password = password
        self.osAuthUrl = osAuthUrl
        self.tenantName = tenantName
        self.privNetName = privNetName
        self.privSubName = privSubName
        self.privSubCidr = privSubCidr
        self.routerName = routerName
        self.neutron = None
        self.network = None
        self.subnet = None
        self.router = None

    def create(self):
        self.neutron = self.neutron_client()
        self.neutron.format = 'json'
        logger.info('Creating neutron network %s...' % self.privNetName)
        self.network = neutron_utils.create_neutron_net(self.neutron, self.privNetName)
        logger.debug("Network '%s' created successfully" % self.network['network']['id'])
        logger.debug('Creating Subnet....')
        self.subnet = neutron_utils.create_neutron_subnet(self.neutron, self.network, self.privSubName,
                                                          self.privSubCidr)

        logger.debug("Subnet '%s' created successfully" % self.subnet['subnets'][0]['id'])
        logger.debug('Creating Router...')
        self.router = neutron_utils.create_neutron_router(self.neutron, self.routerName)

        logger.debug("Router '%s' created successfully" % self.router['router']['id'])
        logger.debug('Adding router to subnet...')

        result = neutron_utils.add_interface_router(self.neutron, self.router, self.subnet)

        if not result:
            raise Exception

    def clean(self):
        neutron_utils.remove_interface_router(self.neutron, self.router, self.subnet)
        neutron_utils.delete_neutron_router(self.neutron, self.router)
        neutron_utils.delete_neutron_subnet(self.neutron, self.subnet)
        neutron_utils.delete_neutron_net(self.neutron, self.network)

    def neutron_client(self):
        """
        Instantiates and returns a client for communications with OpenStack's Neutron server
        :return: the client object
        """
        creds = self.__get_credentials()
        return neutronclient.Client(**creds)

    def __get_credentials(self):
        """
        Returns a creds dictionary object
        :return: the credentials
        """
        return {
            'username': self.username,
            'password': self.password,
            'auth_url': self.osAuthUrl,
            'tenant_name': self.tenantName,
        }

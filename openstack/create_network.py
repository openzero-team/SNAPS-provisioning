import logging

import neutron_utils

logger = logging.getLogger('NeutronNetwork')


class OpenStackNetwork:
    """
    Class responsible for creating a network in OpenStack

    All tasks have been designed after the vPing scenario in the OPNFV functest repository. We will want to make
    this class more flexible, expand it beyond the private network. Additionally, many of the private methods here
    should probably make their way into a file named something like neutron_utils.py.
    """

    def __init__(self, os_creds, name, subnet_settings, router_name):
        """
        Constructor - all parameters are required
        :param os_creds: The credentials to connect with OpenStack
        :param name: The network name
        :param subnet_settings: The settings used to create a subnet object
        :param router_name: The name of the associated router
        """
        self.os_creds = os_creds
        self.name = name
        self.subnet_settings = subnet_settings
        self.router_name = router_name
        self.neutron = neutron_utils.neutron_client(os_creds)
        self.neutron.format = 'json'

        # Attributes instantiated on create()
        self.network = None
        self.subnet = None
        self.router = None
        self.interface_router = None

    def create(self):
        """
        Responsible for creating not only the network but then a private subnet, router, and an interface to the router.
        """
        logger.info('Creating neutron network %s...' % self.name)
        self.network = neutron_utils.create_network(self.neutron, self.name)
        logger.debug("Network '%s' created successfully" % self.network['network']['id'])

        logger.debug('Creating Subnet....')
        self.subnet = neutron_utils.create_subnet(self.neutron, self.subnet_settings, self.network)
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


class SubnetSettings:
    """
    Class representing a subnet
    """

    def __init__(self, cidr, ip_version=4, name=None, tenant_id=None, allocation_pools=dict(), start=None, end=None,
                 gateway_ip=None, enable_dhcp=None, dns_nameservers=list(), host_routes=list(), destination=None,
                 nexthop=None, ipv6_ra_mode=None, ipv6_address_mode=None):
        """
        Constructor - all parameters are optional except cidr (subnet mask)
        :param cidr: The CIDR
        :param ip_version: The IP version, which is 4 or 6.
        :param name: The subnet name.
        :param tenant_id: The ID of the tenant who owns the network. Only administrative users can specify a tenant ID
                          other than their own. You cannot change this value through authorization policies.
        :param allocation_pools: The start and end addresses for the allocation pools.
        :param start: The start address for the allocation pools.
        :param end: The end address for the allocation pools.
        :param gateway_ip: The gateway IP address.
        :param enable_dhcp: Set to true if DHCP is enabled and false if DHCP is disabled.
        :param dns_nameservers: A list of DNS name servers for the subnet. Specify each name server as an IP address
                                and separate multiple entries with a space. For example [8.8.8.7 8.8.8.8].
        :param host_routes: A list of host route dictionaries for the subnet. For example:
                                "host_routes":[
                                    {
                                        "destination":"0.0.0.0/0",
                                        "nexthop":"123.456.78.9"
                                    },
                                    {
                                        "destination":"192.168.0.0/24",
                                        "nexthop":"192.168.0.1"
                                    }
                                ]
        :param destination: The destination for static route
        :param nexthop: The next hop for the destination.
        :param ipv6_ra_mode: A valid value is dhcpv6-stateful, dhcpv6-stateless, or slaac.
        :param ipv6_address_mode: A valid value is dhcpv6-stateful, dhcpv6-stateless, or slaac.
        :return:
        """

        # Required attributes
        self.cidr = cidr
        self.ip_version = ip_version

        # Optional attributes that can be set after instantiation
        self.name = name
        self.tenant_id = tenant_id
        self.allocation_pools = allocation_pools
        self.start = start
        self.end = end
        self.gateway_ip = gateway_ip
        self.enable_dhcp = enable_dhcp
        self.dns_nameservers = dns_nameservers
        self.host_routes = host_routes
        self.destination = destination
        self.nexthop = nexthop
        self.ipv6_ra_mode = ipv6_ra_mode
        self.ipv6_address_mode = ipv6_address_mode

    def dict_for_neutron(self, network):
        """
        Returns a dictionary object representing this object.
        This is meant to be converted into JSON designed for use by the Neutron API
        :param network: (Optional) the network object on which the subnet will be created
        :return: the dictionary object
        """
        out = {
            'cidr': self.cidr,
            'ip_version': self.ip_version,
        }

        if network:
            out['network_id'] = network['network']['id']
        if self.name:
            out['name'] = self.name
        if self.tenant_id:
            out['tenant_id'] = self.tenant_id
        if len(self.allocation_pools) > 0:
            out['allocation_pools'] = self.allocation_pools
        if self.start:
            out['start'] = self.start
        if self.end:
            out['end'] = self.end
        if self.gateway_ip:
            out['gateway_ip'] = self.gateway_ip
        if self.enable_dhcp:
            out['enable_dhcp'] = self.enable_dhcp
        if len(self.dns_nameservers) > 0:
            out['dns_nameservers'] = self.dns_nameservers
        if len(self.host_routes) > 0:
            out['host_routes'] = self.host_routes
        if self.destination:
            out['destination'] = self.destination
        if self.nexthop:
            out['nexthop'] = self.nexthop
        if self.ipv6_ra_mode:
            out['ipv6_ra_mode'] = self.ipv6_ra_mode
        if self.ipv6_address_mode:
            out['ipv6_address_mode'] = self.ipv6_address_mode

        return out


class PortSettings:
    """
    Class representing a subnet
    """

    def __init__(self, name=None, ip_address=None, admin_state_up=True, tenant_id=None, mac_address=None,
                 fixed_ips=dict(), security_groups=None, allowed_address_pairs=dict(), opt_value=None, opt_name=None,
                 device_owner=None, device_id=None):
        """
        Constructor - all parameters are optional
        :param name: A symbolic name for the port.
        :param ip_address: If you specify both a subnet ID and an IP address, OpenStack Networking tries to allocate
                           the specified address to the port.
        :param admin_state_up: The administrative status of the port. True = up / False = down
        :param tenant_id: The ID of the tenant who owns the network. Only administrative users can specify a tenant ID
                          other than their own. You cannot change this value through authorization policies.
        :param mac_address: The MAC address. If you specify an address that is not valid, a Bad Request (400) status
                            code is returned. If you do not specify a MAC address, OpenStack Networking tries to
                            allocate one. If a failure occurs, a Service Unavailable (503) status code is returned.
        :param fixed_ips: If you specify only a subnet ID, OpenStack Networking allocates an available IP from that
                          subnet to the port. If you specify both a subnet ID and an IP address, OpenStack Networking
                          tries to allocate the specified address to the port
        :param security_groups: One or more security group IDs.
        :param allowed_address_pairs: A set of zero or more allowed address pairs. An address pair contains an IP
                                      address and MAC address.
        :param opt_value: The extra DHCP option value.
        :param opt_name: The extra DHCP option name.
        :param device_owner: The ID of the entity that uses this port. For example, a DHCP agent.
        :param device_id: The ID of the device that uses this port. For example, a virtual server.
        :return:
        """

        self.name = name
        self.ip_address = ip_address
        self.admin_state_up = admin_state_up
        self.tenant_id = tenant_id
        self.mac_address = mac_address
        self.fixed_ips = fixed_ips
        self.security_groups = security_groups
        self.allowed_address_pairs = allowed_address_pairs
        self.opt_value = opt_value
        self.opt_name = opt_name
        self.device_owner = device_owner
        self.device_id = device_id

    def dict_for_neutron(self, network=None, subnet=None):
        """
        Returns a dictionary object representing this object.
        This is meant to be converted into JSON designed for use by the Neutron API

        TODO - expand automated testing to exercise all parameters

        :param network: (Optional) the network object on which the port will be created
        :param subnet: (Optional) the subnet object on which the port will be created
        :return: the dictionary object
        """
        out = {'admin_state_up': self.admin_state_up}

        if network:
            out['network_id'] = network['network']['id']
        # TODO/FIXME - specs say this is key/value is optional but the API call fails
        # if subnet:
        #     if len(subnet['subnets']) > 0:
        #         sub = subnet['subnets']
        #         out['subnet_id'] = sub[0]['id']
        if self.name:
            out['name'] = self.name
        if self.ip_address and not self.fixed_ips:
            out['fixed_ips'] = [{"ip_address": self.ip_address}]
        if self.tenant_id:
            out['tenant_id'] = self.tenant_id
        if self.mac_address:
            out['mac_address'] = self.mac_address
        if len(self.fixed_ips) > 0:
            out['fixed_ips'] = self.fixed_ips
            if self.ip_address:
                # TODO/FIXME - this hasn't been tested and looks to be dangerous
                out['fixed_ips'].append({"ip_address": self.ip_address})
        if self.security_groups:
            out['security_groups'] = self.security_groups
        if len(self.allowed_address_pairs) > 0:
            out['allowed_address_pairs'] = self.allowed_address_pairs
        if self.opt_value:
            out['opt_value'] = self.opt_value
        if self.opt_name:
            out['opt_name'] = self.opt_name
        if self.device_owner:
            out['device_owner'] = self.device_owner
        if self.device_id:
            out['device_id'] = self.device_id

        return {'port': out}

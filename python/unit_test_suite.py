import unittest
import logging
import sys

from tests import file_utils_tests
from openstack.tests.create_image_tests import CreateImageSuccessTests, CreateImageNegativeTests
from openstack.tests.os_source_file_test import OSSourceFileTestsCase
from openstack.tests.neutron_utils_tests import NeutronUtilsTests
from openstack.tests.create_network_tests import CreateNetworkSuccessTests
from openstack.tests.nova_utils_tests import NovaUtilsKeypairTests
from openstack.tests.create_keypairs_tests import CreateKeypairsTests
from openstack.tests.create_instance_tests import CreateInstanceSingleNetworkTests
from openstack.tests.create_instance_tests import CreateInstancePubPrivNetTests
from provisioning.tests.ansible_utils_tests import AnsibleProvisioningTests

__author__ = 'spisarski'

logger = logging.getLogger('unit_test_suite')


def create_test_suite(source_filename=None, proxy_settings=None):
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromModule(file_utils_tests))
    suite.addTest(OSSourceFileTestsCase.parameterize(CreateImageSuccessTests, source_filename, proxy_settings))
    suite.addTest(OSSourceFileTestsCase.parameterize(CreateImageNegativeTests, source_filename, proxy_settings))
    suite.addTest(OSSourceFileTestsCase.parameterize(NeutronUtilsTests, source_filename, proxy_settings))
    suite.addTest(OSSourceFileTestsCase.parameterize(CreateNetworkSuccessTests, source_filename, proxy_settings))
    suite.addTest(OSSourceFileTestsCase.parameterize(NovaUtilsKeypairTests, source_filename, proxy_settings))
    suite.addTest(OSSourceFileTestsCase.parameterize(CreateKeypairsTests, source_filename, proxy_settings))
    suite.addTest(OSSourceFileTestsCase.parameterize(CreateInstanceSingleNetworkTests, source_filename, proxy_settings))
    suite.addTest(OSSourceFileTestsCase.parameterize(CreateInstancePubPrivNetTests, source_filename, proxy_settings))
    suite.addTest(OSSourceFileTestsCase.parameterize(AnsibleProvisioningTests, source_filename, proxy_settings))
    return suite


def main():
    """
    Begins running unit tests.
    argv[1] if used must be the source filename else os_env.yaml will be leveraged instead
    argv[2] if used must be the proxy server <host>:<port>
    """
    logging.basicConfig(level=logging.DEBUG)
    logger.info('Starting test suite')

    if len(sys.argv) > 1:
        if len(sys.argv) > 2:
            suite = create_test_suite(sys.argv[1], sys.argv[2])
        else:
            suite = create_test_suite(sys.argv[1])
    else:
        suite = create_test_suite()

    result = unittest.TextTestRunner(verbosity=2).run(suite)

    if result.errors:
        logger.error('Number of errors in test suite - ' + str(len(result.errors)))
        for test, message in result.errors:
            logger.error(str(test) + " ERROR with " + message)

    if result.failures:
        logger.error('Number of failures in test suite - ' + str(len(result.failures)))
        for test, message in result.failures:
            logger.error(str(test) + " FAILED with " + message)

    if (result.errors and len(result.errors) > 0) or (result.failures and len(result.failures) > 0):
        exit(1)

    exit(0)


if __name__ == '__main__':
    main()

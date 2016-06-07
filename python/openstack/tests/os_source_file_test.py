import unittest
import openstack_tests


class OSSourceFileTestsCase(unittest.TestCase):
    """
    Super for test classes requiring a connection to OpenStack
    """
    def __init__(self, method_name='runTest', os_env_file=None, proxy_settings=None):
        super(OSSourceFileTestsCase, self).__init__(method_name)
        self.os_creds = openstack_tests.get_credentials(os_env_file, proxy_settings)

    @staticmethod
    def parameterize(testcase_klass, os_env_file=None, proxy_settings=None):
        """ Create a suite containing all tests taken from the given
            subclass, passing them the parameter 'param'.
        """
        test_loader = unittest.TestLoader()
        test_names = test_loader.getTestCaseNames(testcase_klass)
        suite = unittest.TestSuite()
        for name in test_names:
            suite.addTest(testcase_klass(name, os_env_file, proxy_settings))
        return suite

import unittest
import openstack.nova_utils as nova_utils
import logging
import openstack_tests
from Crypto.PublicKey import RSA
import os

# Initialize Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('nova_utils_tests')

os_creds = openstack_tests.get_credentials()

priv_key_file_path = '/tmp/testKey'
pub_key_file_path = priv_key_file_path + '.pub'


class NovaUtilsKeypairTests(unittest.TestCase):
    """
    Test for the CreateImage class defined in create_image.py
    """

    def setUp(self):
        """
        Instantiates the CreateImage object that is responsible for downloading and creating an OS image file
        within OpenStack
        """
        self.nova = nova_utils.nova_client(os_creds)
        self.keys = RSA.generate(1024)
        self.public_key = self.keys.publickey().exportKey('OpenSSH')
        self.keypair_name = 'testKP'
        self.keypair = None

    def tearDown(self):
        """
        Cleans the image and downloaded image file
        """
        if self.keypair:
            try:
                nova_utils.delete_keypair(self.nova, self.keypair)
            except:
                pass

        try:
            os.remove(priv_key_file_path)
        except:
            pass

        try:
            os.remove(priv_key_file_path + '.pub')
        except:
            pass

    def test_create_keypair(self):
        """
        Tests the creation of an OpenStack keypair that does not exist.
        """
        self.keypair = nova_utils.upload_keypair(self.nova, self.keypair_name, self.public_key)
        result = nova_utils.keypair_exists(self.nova, self.keypair)
        self.assertEquals(self.keypair, result)
        keypairs = nova_utils.get_keypairs(self.nova)
        for kp in keypairs:
            if kp.id == self.keypair.id:
                return
        self.fail('Keypair not found')

    def test_create_delete_keypair(self):
        """
        Tests the creation of an OpenStack keypair that does not exist.
        """
        self.keypair = nova_utils.upload_keypair(self.nova, self.keypair_name, self.public_key)
        result = nova_utils.keypair_exists(self.nova, self.keypair)
        self.assertEquals(self.keypair, result)
        nova_utils.delete_keypair(self.nova, self.keypair)
        result2 = nova_utils.keypair_exists(self.nova, self.keypair)
        self.assertIsNone(result2)

    def test_create_key_from_file(self):
        """
        Tests that the generated RSA keys are properly saved to files
        :return:
        """
        nova_utils.save_keys_to_files(self.keys, priv_key_file_path, pub_key_file_path)
        self.keypair = nova_utils.upload_keypair_file(self.nova, self.keypair_name, pub_key_file_path)
        pub_key = open(os.path.expanduser(pub_key_file_path)).read()
        self.assertEquals(self.keypair.public_key, pub_key)
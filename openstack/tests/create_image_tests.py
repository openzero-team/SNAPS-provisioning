import unittest
import os

import file_utils
import openstack.create_image as create_image
from openstack import os_credentials

# This is currently pointing to the CL OPNFV Lab 2 environment and these tests will break should there not be network
# connectivity to this location.
os_auth_url = 'http://10.197.123.37:5000/v2.0'
username = 'admin'
password = 'octopus'
tenant_name = 'admin'
os_creds = os_credentials.OSCreds(username, password, os_auth_url, tenant_name)

image_format = 'qcow2'
image_url = 'http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img'
image_name = 'test-image'
download_path = '/tmp/create_image_tests'


class CreateImageSuccessTests(unittest.TestCase):
    """
    Test for the CreateImage class defined in create_image.py
    """

    def setUp(self):
        """
        Instantiates the CreateImage object that is responsible for downloading and creating an OS image file
        within OpenStack
        """
        self.os_image = create_image.OpenStackImage(os_creds, image_format, image_url, image_name, download_path)

    def tearDown(self):
        """
        Cleans the image and downloaded image file
        """
        self.os_image.clean()

    def testCreateImageClean(self):
        """
        Tests the creation of an OpenStack image when the download directory does not exist.
        """
        # Create Image
        self.os_image.create()
        glance = self.os_image.glance
        images = glance.images.list()

        # Validate
        found = False
        for image in images:
            if image.name == self.os_image.image_name:
                found = True

        self.assertEquals(True, found)

    def testCreateImageWithExistingDownloadDirectory(self):
        """
        Tests the creation of an OpenStack image when the image file directory exists but not the image file.
        """
        # Create download directory
        os.makedirs(download_path)

        # Create Image
        self.os_image.create()
        glance = self.os_image.glance
        images = glance.images.list()

        # Validate
        found = False
        for image in images:
            if image.name == self.os_image.image_name:
                found = True

        self.assertEquals(True, found)

    def testCreateImageWithExistingImageFile(self):
        """
        Tests the creation of an OpenStack image when the image file exists.
        """
        # Create download directory
        os.makedirs(download_path)

        # Download image file
        file_utils.download(image_url, download_path)

        # Create Image
        self.os_image.create()
        glance = self.os_image.glance
        images = glance.images.list()

        # Validate
        found = False
        for image in images:
            if image.name == self.os_image.image_name:
                found = True

        self.assertEquals(True, found)


class CreateImageNegativeTests(unittest.TestCase):
    """
    Negative test cases for the CreateImage class
    """

    def setUp(self):
        self.createImage = None

    def tearDown(self):
        if self.createImage is not None:
            self.createImage.clean()

    def testInvalidDirectory(self):
        """
        Expect an exception when the download destination path cannot be created
        """
        self.createImage = create_image.OpenStackImage(os_creds, image_format,image_url, image_name, '/foo')
        with self.assertRaises(Exception):
            self.createImage.create()

    def testNoneImageName(self):
        """
        Expect an exception when the image name is None
        """
        self.createImage = create_image.OpenStackImage(os_creds, image_format, image_url, None, download_path)
        with self.assertRaises(Exception):
            self.createImage.create()

    def testBadImageUrl(self):
        """
        Expect an exception when the image download url is bad
        """
        self.createImage = create_image.OpenStackImage(os_creds, image_format, 'http://bad.url.com/bad.iso', image_name,
                                                       download_path)
        with self.assertRaises(Exception):
            self.createImage.create()

    def testNoneTenantName(self):
        """
        Expect an exception when the tenant name is None
        """
        with self.assertRaises(Exception):
            self.createImage = create_image.OpenStackImage(os_credentials.OSCreds(username, password, os_auth_url,
                                                                                  None),
                                                           image_format, image_url, image_name, download_path)

    def testNoneAuthUrl(self):
        """
        Expect an exception when the tenant name is None
        """
        with self.assertRaises(Exception):
            self.createImage = create_image.OpenStackImage(os_credentials.OSCreds(username, password, None,
                                                                                  tenant_name),
                                                           image_format, image_url, image_name, download_path)

    def testNonePassword(self):
        """
        Expect an exception when the tenant name is None
        """
        with self.assertRaises(Exception):
            self.createImage = create_image.OpenStackImage(os_credentials.OSCreds(username, None, os_auth_url,
                                                                                  tenant_name),
                                                           image_format, image_url, image_name, download_path)

    def testNoneUser(self):
        """
        Expect an exception when the tenant name is None
        """
        with self.assertRaises(Exception):
            self.createImage = create_image.OpenStackImage(os_credentials.OSCreds(None, password, os_auth_url,
                                                                                  tenant_name),
                                                           image_format, image_url, image_name, download_path)

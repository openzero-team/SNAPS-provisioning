import unittest
import openstack.create_image as createImage

class CreateImageTests(unittest.TestCase):

    def setUp(self):
        print 'Setting up'
        self.createImage = createImage.CreateImage('testImage',
                                                   'http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img',
                                                   'qcow2', '/bar')

    def test1(self):
        self.createImage.create()

    def test2(self):
        print 'Test 2'
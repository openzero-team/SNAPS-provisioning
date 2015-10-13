import unittest
import openstack.create_image as createImage

class CreateImageTests(unittest.TestCase):

    def setUp(self):
        print 'Setting up'
        self.createImage = createImage.CreateImage('testImage', 'http://foo.com', 'qcow2', '/bar')

    def test1(self):
        print 'Test 1'
    def test2(self):
        print 'Test 2'
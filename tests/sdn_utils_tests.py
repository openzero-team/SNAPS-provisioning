import os
import unittest
import shutil

import sdn_utils


class SdnUtilsTests(unittest.TestCase):
    """
    Tests the methods in sdn_utils.py
    """

    def setUp(self):
        self.tmpDir = '/tmp/sdntests'
        if not os.path.exists(self.tmpDir):
            os.makedirs(self.tmpDir)

        self.tmpFile = self.tmpDir + '/bar.txt'
        if not os.path.exists(self.tmpFile):
            open(self.tmpFile, 'wb')

    def tearDown(self):
        if os.path.exists(self.tmpDir) and os.path.isdir(self.tmpDir):
            shutil.rmtree(self.tmpDir)

    def testFileIsDirectory(self):
        """
        Ensure the sdn_util.fileExists() method returns false with a directory
        """
        result = sdn_utils.fileExists(self.tmpDir)
        self.assertFalse(result)
        # TODO - Cleanup directory

    def testFileNotExist(self):
        """
        Ensure the sdn_util.fileExists() method returns false with a bogus file
        """
        result = sdn_utils.fileExists('/foo/bar.txt')
        self.assertFalse(result)

    def testFileExists(self):
        """
        Ensure the sdn_util.fileExists() method returns false with a directory
        """
        if not os.path.exists(self.tmpFile):
            os.makedirs(self.tmpFile)

        result = sdn_utils.fileExists(self.tmpFile)
        self.assertTrue(result)

    def testDownloadBadUrl(self):
        """
        Tests the sdn_util.download() method when given a bad URL
        """
        with self.assertRaises(Exception):
            sdn_utils.download('http://bunkUrl.com/foo/bar.iso', self.tmpDir)

    def testDownloadBadDir(self):
        """
        Tests the sdn_util.download() method when given a bad URL
        """
        with self.assertRaises(Exception):
            sdn_utils.download('http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img', '/foo/bar')

    def testCirrosImageDownload(self):
        """
        Tests the sdn_util.download() method when given a good Cirros QCOW2 URL
        """
        imageFile = sdn_utils.download('http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img',
                                       self.tmpDir)
        self.assertIsNotNone(imageFile)
        self.assertTrue(imageFile.name.endswith("cirros-0.3.4-x86_64-disk.img"))
        self.assertTrue(imageFile.name.startswith(self.tmpDir))

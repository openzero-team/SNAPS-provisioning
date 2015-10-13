import sdn_utils, os, unittest

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
        if os.path.exists(self.tmpFile) and os.path.isfile(self.tmpFile):
            os.remove(self.tmpFile)

        if os.path.exists(self.tmpDir) and os.path.isdir(self.tmpDir):
            os.rmdir(self.tmpDir)

    def testFileIsDirectory(self):
        """
        Ensure the fileExists() method returns false with a directory
        """
        result = sdn_utils.fileExists(self.tmpDir)
        self.assertFalse(result)
        # TODO - Cleanup directory

    def testFileNotExist(self):
        """
        Ensure the fileExists() method returns false with a bogus file
        """
        result = sdn_utils.fileExists("/foo/bar.txt")
        self.assertFalse(result)

    def testFileExists(self):
        """
        Ensure the fileExists() method returns false with a directory
        """
        if not os.path.exists(self.tmpFile):
            os.makedirs(self.tmpFile)

        # os.open(self.tmpFile)
        result = sdn_utils.fileExists(self.tmpFile)
        self.assertTrue(result)
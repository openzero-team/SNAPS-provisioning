# Copyright (c) 2016 Cable Television Laboratories, Inc. ("CableLabs")
#                    and others.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
__author__ = 'spisarski'

import os
import unittest
import shutil

import file_utils


class SdnUtilsTests(unittest.TestCase):
    """
    Tests the methods in file_utils.py
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
        result = file_utils.file_exists(self.tmpDir)
        self.assertFalse(result)
        # TODO - Cleanup directory

    def testFileNotExist(self):
        """
        Ensure the sdn_util.fileExists() method returns false with a bogus file
        """
        result = file_utils.file_exists('/foo/bar.txt')
        self.assertFalse(result)

    def testFileExists(self):
        """
        Ensure the sdn_util.fileExists() method returns false with a directory
        """
        if not os.path.exists(self.tmpFile):
            os.makedirs(self.tmpFile)

        result = file_utils.file_exists(self.tmpFile)
        self.assertTrue(result)

    def testDownloadBadUrl(self):
        """
        Tests the sdn_util.download() method when given a bad URL
        """
        with self.assertRaises(Exception):
            file_utils.download('http://bunkUrl.com/foo/bar.iso', self.tmpDir)

    def testDownloadBadDir(self):
        """
        Tests the sdn_util.download() method when given a bad URL
        """
        with self.assertRaises(Exception):
            file_utils.download('http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img', '/foo/bar')

    def testCirrosImageDownload(self):
        """
        Tests the sdn_util.download() method when given a good Cirros QCOW2 URL
        """
        imageFile = file_utils.download('http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img',
                                       self.tmpDir)
        self.assertIsNotNone(imageFile)
        self.assertTrue(imageFile.name.endswith("cirros-0.3.4-x86_64-disk.img"))
        self.assertTrue(imageFile.name.startswith(self.tmpDir))

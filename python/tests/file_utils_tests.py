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
import os
import unittest
import shutil

import file_utils

__author__ = 'spisarski'


class FileUtilsTests(unittest.TestCase):
    """
    Tests the methods in file_utils.py
    """

    def setUp(self):
        self.tmpDir = '/tmp/file_utils_tests'
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
        Ensure the file_utils.fileExists() method returns false with a directory
        """
        result = file_utils.file_exists(self.tmpDir)
        self.assertFalse(result)
        # TODO - Cleanup directory

    def testFileNotExist(self):
        """
        Ensure the file_utils.fileExists() method returns false with a bogus file
        """
        result = file_utils.file_exists('/foo/bar.txt')
        self.assertFalse(result)

    def testFileExists(self):
        """
        Ensure the file_utils.fileExists() method returns false with a directory
        """
        if not os.path.exists(self.tmpFile):
            os.makedirs(self.tmpFile)

        result = file_utils.file_exists(self.tmpFile)
        self.assertTrue(result)

    def testDownloadBadUrl(self):
        """
        Tests the file_utils.download() method when given a bad URL
        """
        with self.assertRaises(Exception):
            file_utils.download('http://bunkUrl.com/foo/bar.iso', self.tmpDir)

    def testDownloadBadDir(self):
        """
        Tests the file_utils.download() method when given a bad URL
        """
        with self.assertRaises(Exception):
            file_utils.download('http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img', '/foo/bar')

    def testCirrosImageDownload(self):
        """
        Tests the file_utils.download() method when given a good Cirros QCOW2 URL
        """
        image_file = file_utils.download('http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img',
                                         self.tmpDir)
        self.assertIsNotNone(image_file)
        self.assertTrue(image_file.name.endswith("cirros-0.3.4-x86_64-disk.img"))
        self.assertTrue(image_file.name.startswith(self.tmpDir))

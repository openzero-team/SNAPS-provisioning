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

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Virtual Environment Deployment, Provisioning, and Testing Framework',
    'author': 'Steve Pisarski',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 's.pisarski@cablelabs.com',
    'version': '0.1',
    'install_requires': ['python-keystoneclient', 'python-glanceclient', 'python-neutronclient', 'python-novaclient',
                         'scp', 'PyYAML', 'ansible==2.1.0', 'Crypto', 'passlib',],
    'packages': ['NAME'],
    'scripts': [],
    'name': 'provisioning'
}

# setup(**config, requires=['ansible', 'Crypto', 'python-keystoneclient', 'scp', 'PyYAML'])
setup(**config)
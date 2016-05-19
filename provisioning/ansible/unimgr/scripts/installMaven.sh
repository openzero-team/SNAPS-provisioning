#!/usr/bin/env bash
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

echo "Installing apache-maven-3.3.3" >> ~/mdsal_ansible/install.log
mkdir ~/mdsal_ansible
mkdir ~/mdsal_ansible/Downloads
cd ~/mdsal_ansible/Downloads
wget http://ftp.wayne.edu/apache/maven/maven-3/3.3.3/binaries/apache-maven-3.3.3-bin.tar.gz
mkdir /opt/maven
tar -xzvf ~/mdsal_ansible/Downloads/apache-maven-3.3.3-bin.tar.gz
mv apache-maven-3.3.3 /opt/maven
ln -s /opt/maven/apache-maven-3.3.3/bin/mvn /usr/bin/mvn

cd ~

wget https://raw.githubusercontent.com/opendaylight/odlparent/master/settings.xml

if [ ! -d ~/.m2/ ]; then
    mkdir ~/.m2/
fi

cp settings.xml ~/.m2/
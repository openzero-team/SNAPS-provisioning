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

adduser ovs
#su - ovs
#whoami >> ~/ovs.out

runuser -l ovs -c 'mkdir -p ~ovs/rpmbuild/SOURCES'

runuser -l ovs -c 'wget http://openvswitch.org/releases/openvswitch-2.3.2.tar.gz'
runuser -l ovs -c 'cp openvswitch-2.3.2.tar.gz ~ovs'
echo 'Downloaded openvswitch-2.3.2.tar.gz' >> ~/ovs.out

runuser -l ovs -c 'cp ~ovs/openvswitch-2.3.2.tar.gz ~ovs/rpmbuild/SOURCES/'
echo 'Copied ovs tar to ~ovs/rpmbuild/SOURCES' >> ~/ovs.out

cd ~ovs
runuser -l ovs -c 'tar xfz openvswitch-2.3.2.tar.gz'
echo 'Extracted ovs tar' >> ~/ovs.out

sed 's/openvswitch-kmod, //g' ~ovs/openvswitch-2.3.2/rhel/openvswitch.spec > ~ovs/openvswitch-2.3.2/rhel/openvswitch_no_kmod.spec

chown ovs:ovs ~ovs/openvswitch-2.3.2/rhel/openvswitch_no_kmod.spec

runuser -l ovs -c 'rpmbuild -bb --nocheck openvswitch-2.3.2/rhel/openvswitch_no_kmod.spec'
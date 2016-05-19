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

mkdir /etc/openvswitch

yum -y localinstall ~ovs/rpmbuild/RPMS/x86_64/openvswitch-2.3.2-1.x86_64.rpm

yum -y install policycoreutils-python

semanage fcontext -a -t openvswitch_rw_t "/etc/openvswitch(/.*)?"
restorecon -Rv /etc/openvswitch

systemctl start openvswitch.service
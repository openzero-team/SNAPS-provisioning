#!/bin/sh
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
#
# Script 1 - Set the environment variables for the project

echo "export M2_HOME=/opt/maven/apache-maven-3.3.3" >> $HOME/.bashrc
echo "export MAVEN_OPTS='-Xmx2048m -XX:MaxPermSize=1024m'" >> $HOME/.bashrc
echo "export JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk-1.7.0.95-2.6.4.0.el7_2.x86_64" >> $HOME/.bashrc
echo "export CATALINA_HOME=/usr/local/apache-tomcat/apache-tomcat-8.0.24" >> $HOME/.bashrc
echo "done executing" >> $HOME/environment.log
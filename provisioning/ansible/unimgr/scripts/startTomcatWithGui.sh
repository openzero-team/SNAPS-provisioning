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
# Script 5 - Copy war files to tomcat and start Tomcat

CATALINA_HOME='/usr/local/apache-tomcat/apache-tomcat-8.0.24'
echo "Copying war files" >>  ~/mdsal_ansible/install.log
echo $CATALINA_HOME >> ~/mdsal_ansible/install.log

mkdir ~/mdsal_ansible/Downloads
cd ~/mdsal_ansible/Downloads
wget http://archive.apache.org/dist/tomcat/tomcat-8/v8.0.24/bin/apache-tomcat-8.0.24.tar.gz
mkdir /usr/local/apache-tomcat
sudo tar -xzvf ~/mdsal_ansible/Downloads/apache-tomcat-8.0.24.tar.gz -C /usr/local/apache-tomcat/
sudo sed -i 's/Connector port="8080"/Connector port="9090"/'  $CATALINA_HOME/conf/server.xml

sudo cp ~/mdsal_ansible/lsoapi/cos/cosmgr/target/cosmgr.war $CATALINA_HOME/webapps/.
sudo cp ~/mdsal_ansible/lsoapi/evc/evcmgr/target/evcmgr.war $CATALINA_HOME/webapps/.
sudo cp ~/mdsal_ansible/lsoapi/svc/svcmgr/target/svcmgr.war $CATALINA_HOME/webapps/.

sudo $CATALINA_HOME/bin/shutdown.sh &
nohup sudo $CATALINA_HOME/bin/startup.sh &

echo "Tomcat started" >>  ~/mdsal_ansible/install.log
cd ~/mdsal_ansible/lsoapi/demo-ui
sudo npm install >>  ~/mdsal_ansible/lsoapi.log


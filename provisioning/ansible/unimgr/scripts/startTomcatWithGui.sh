#!/bin/sh
# Script 5 - Copy war files to tomcat and start Tomcat

CATALINA_HOME='/usr/local/apache-tomcat/apache-tomcat-8.0.24'
echo "Copying war files" >>  ~/mdsal_ansible/install.log
echo $CATALINA_HOME >> ~/mdsal_ansible/install.log
cd ~/mdsal_ansible/lsoapi
sudo cp ./cos/cosmgr/target/cosmgr.war $CATALINA_HOME/webapps/.
sudo cp ./evc/evcmgr/target/evcmgr.war $CATALINA_HOME/webapps/.
sudo cp ./svc/svcmgr/target/svcmgr.war $CATALINA_HOME/webapps/.
sudo $CATALINA_HOME/bin/shutdown.sh &
nohup sudo $CATALINA_HOME/bin/startup.sh &

echo "Tomcat started" >>  ~/mdsal_ansible/install.log
cd ~/mdsal_ansible/lsoapi/demo-ui
sudo npm install >>  ~/mdsal_ansible/lsoapi.log


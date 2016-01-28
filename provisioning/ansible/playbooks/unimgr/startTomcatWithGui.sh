#!/bin/sh
# Script 5 - Copy war files to tomcat and start Tomcat

home='/home/vbcpe'  # change this to your home directory path
CATALINA_HOME='/usr/local/apache-tomcat/apache-tomcat-8.0.24'
echo "Copying war files" >>  $home/mdsal_ansible/install.log
echo $CATALINA_HOME >> $home/mdsal_ansible/install.log
cd $home/mdsal_ansible/lsoapi
sudo cp ./cos/cosmgr/target/cosmgr.war $CATALINA_HOME/webapps/.
sudo cp ./evc/evcmgr/target/evcmgr.war $CATALINA_HOME/webapps/.
sudo cp ./svc/svcmgr/target/svcmgr.war $CATALINA_HOME/webapps/.
sudo $CATALINA_HOME/bin/shutdown.sh &
nohup sudo $CATALINA_HOME/bin/startup.sh &

echo "Tomcat started" >>  $home/mdsal_ansible/install.log
cd $home/mdsal_ansible/lsoapi/demo-ui
sudo npm install >>  $home/mdsal_ansible/lsoapi.log


#!/bin/sh
# Script 3 - Install Java, Tomcat, Maven, bower, grunt, and less

home='/home/vbcpe'  # change this to your home directory path
CATALINA_HOME='/usr/local/apache-tomcat/apache-tomcat-8.0.24'

sudo mkdir -p /usr/local 
cd /usr/local
sudo mkdir apache-maven
sudo mkdir apache-tomcat
sudo mkdir java

echo "Installing apache-maven-3.3.3" >> $home/mdsal_ansible/install.log 
sudo tar -xzvf $home/mdsal_ansible/Downloads/apache-maven-3.3.3-bin.tar.gz -C /usr/local/apache-maven/
sudo update-alternatives --install /usr/bin/mvn mvn /usr/local/apache-maven/apache-maven-3.3.3/bin/mvn 1
sudo update-alternatives --config mvn

echo "Installing apache-tomcat-8.0.24" >> $home/mdsal_ansible/install.log 
sudo tar -xzvf $home/mdsal_ansible/Downloads/apache-tomcat-8.0.24.tar.gz -C /usr/local/apache-tomcat/
sudo sed -i 's/Connector port="8080"/Connector port="9090"/'  $CATALINA_HOME/conf/server.xml

echo "Installing JAVA 7u79" >> $home/mdsal_ansible/install.log 
sudo tar -xzvf $home/mdsal_ansible/Downloads/jdk-7u79-linux-x64.tar.gz -C /usr/local/java/
sudo update-alternatives --install "/usr/bin/java" "java" "/usr/local/java/jdk1.7.0_79/bin/java" 1
sudo update-alternatives --install "/usr/bin/javac" "javac" "/usr/local/java/jdk1.7.0_79/bin/javac" 1
sudo update-alternatives --set java /usr/local/java/jdk1.7.0_79/bin/java
sudo update-alternatives --set javac /usr/local/java/jdk1.7.0_79/bin/javac


cd $home/mdsal_ansible/Downloads
sudo rm -rf *.gz

echo "Deleted downloads" >> $home/mdsal_ansible/install.log 
sudo apt-get install nodejs-legacy npm # comment this line when used with ansible
sudo npm install bower -g
sudo npm install grunt-cli -g
sudo npm install less -g

echo "Done" >> $home/mdsal_ansible/install.log 


#!/bin/sh
# Script 2 - Clone all relevant repositories and download Java 1.7u79, Maven 3.3.3, Tomcat 8.0.24

mkdir -p $HOME/mdsal_ansible
touch $HOME/mdsal_ansible/install.log
echo "Starting script" >> $HOME/mdsal_ansible/install.log 
cd
mkdir -p $HOME/mdsal_ansible
cd mdsal_ansible
#git clone https://git.opendaylight.org/gerrit/odlparent  
#git clone https://git.opendaylight.org/gerrit/yangtools  
#git clone https://git.opendaylight.org/gerrit/controller  
git clone https://git.opendaylight.org/gerrit/unimgr
git clone https://gerrit.opnfv.org/gerrit/lsoapi 
echo "Cloning ODL done" >> $HOME/mdsal_ansible/install.log 

mkdir -p $HOME/mdsal_ansible/Downloads
cd $HOME/mdsal_ansible/Downloads
wget http://ftp.wayne.edu/apache/maven/maven-3/3.3.3/binaries/apache-maven-3.3.3-bin.tar.gz 
wget http://archive.apache.org/dist/tomcat/tomcat-8/v8.0.24/bin/apache-tomcat-8.0.24.tar.gz
wget -nv --no-check-certificate --no-cookies --header "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/7u79-b15/jdk-7u79-linux-x64.tar.gz

echo "Making relevant directories" >> $HOME/mdsal_ansible/install.log 


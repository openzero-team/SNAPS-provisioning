#!/bin/sh
# Script 1 - Set the environment variables for the project

echo "export M2_HOME=/usr/local/apache-maven/apache-maven-3.3.3" >> $HOME/.bash_profile
echo "export MAVEN_OPTS='-Xmx2048m -XX:MaxPermSize=1024m'" >> $HOME/.bash_profile
echo "export JAVA_HOME=/usr/local/java/jdk1.7.0_79" >> $HOME/.bash_profile
echo "export CATALINA_HOME=/usr/local/apache-tomcat/apache-tomcat-8.0.24" >> $HOME/.bash_profile
echo "done executing" >> $HOME/environment.log
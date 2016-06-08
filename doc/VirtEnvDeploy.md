# Overview
The main purpose of this project is to enable one to describe a virtual environment in a YAML file and enable the
user to deploy it to an OpenStack cloud in a repeatable manner. There are also options to un-deploy that same
environment by leveraging the original YAML file.

# To deploy/clean virtual environments
  * cd <repo dir> python
    (CWD must be here now as there are some post-deployment Ansible scripts located in python/provisioning/ansible
     called by create_instance.py
  * export PYTHONPATH=$PYTHONPATH:$(pwd)
  * Deploy
    * python deploy_venv.py -e <path to deployment configuration YAML file> -d
    * Working example (deployment of a virtual environment where the VM has Yardstick installed):

```
python deploy_venv.py -e <path to repo>/ansible/yardstick/deploy-yardstick.yaml -d
```
      
# Environment Configuration YAML File
more to come...
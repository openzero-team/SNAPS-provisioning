As many of the tests and environment deployments leverage Ansible 1.9.4, the host on which these scripts will run must
 be configured to disable StrictHostKeyChecking. This should no longer be required once the code has been migrated to
 use the Ansible 2.0 APIs. Additionally, should your OpenStack environment be accessible via a proxy server, the
 ProxyCommand must be set. This is done by editing the ~/.ssh/config file.
 
* Setting to avoid entries into ~/.ssh/known_hosts which generally requires a prompt but is not available
 when executing an Ansible Playbook via the Python APIs:
 

    ```
    Host <IP or Subnet (IP with wildcard) in question>
        StrictHostKeyChecking no
        UserKnownHostsFile=/dev/null
    ```

* Setting when accessing VMs behind a proxy:


    ```
    Host <IP or Subnet (IP with wildcard) in question>
        ProxyCommand ~/.ssh/corkscrew <proxy host> <proxy port> %h %p
    ```
    
** Note: The corkscrew checked into the ./ansible/conf/ssh directory has been complied on OS X

As many of the tests and environment deployments leverage Ansible 2.1.0,
Additionally, should your OpenStack environment be accessible via a proxy server, the
 ProxyCommand must be set. This is done by editing the ~/.ssh/config file.

* Setting when accessing VMs behind a proxy:


    ```
    Host <IP or Subnet (IP with wildcard) in question>
        ProxyCommand ~/.ssh/corkscrew <proxy host> <proxy port> %h %p
    ```
    
** Note: The corkscrew checked into the ./ansible/conf/ssh directory has been complied on OS X

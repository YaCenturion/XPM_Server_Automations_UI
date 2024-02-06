# `>` VMs Tools

These are various tools for use for VMs.
Latest stable version: http://vms.expim.local


# `>` Imortant Docker preset

Before deploy:
- `sudo systemctl stop docker`
- create `/etc/docker/daemon.json`
- insert code:
  * ```
    {
      "bip": "172.18.0.1/16"
    }
    ```
    > because `172.17.*.*` used for internal IP address
- `sudo systemctl start docker`
- `ip route` & `docker network ls` u will see like this:
  + ```
    $ ip route
    default via 172.16.5.1 dev ens3 proto static
    172.16.5.0/24 dev ens3 proto kernel scope link src 172.16.5.20
    172.18.0.0/16 dev docker0 proto kernel scope link src 172.18.0.1
    172.27.0.0/16 dev br-e3a3944d96f7 proto kernel scope link src 172.27.0.1
    
    $ docker network ls
    NETWORK ID     NAME      DRIVER    SCOPE
    c9a335e78438   bridge    bridge    local
    e3a3944d96f7   docknet   bridge    local
    61cadd40fe45   host      host      local
    6568df916d4b   none      null      local
    ``` 
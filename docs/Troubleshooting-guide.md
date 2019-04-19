# Troubleshooting-guide

## Docker

Run this command to list Docker images 
```
$ docker image
```
Run this command to list running containers
```
$ docker ps
```
Run this command to list all containers
```
$ docker ps -a
```
Run this command to list containers
```
$ docker-compose ps
```
Run this command to list networks
```
$ docker network ls
```

## SaltStack

Run this command to check the salt-master service status
``` 
docker exec -it master service salt-master status
```
Run this command to check the salt-minion service status
```
docker exec -it minion1 service salt-minion status
```
Run this command to list the keys accepted by the master
```
docker exec -it master salt-key -L
```
Run this command to validate master configuration
```
docker exec -it master more /etc/salt/master
```
Run this command to check the other salt files on the master (pillar, runner, ...)
```
docker exec -it master ls /srv/
```
Run this command to validate minion configuration 
```
docker exec -it minion1 more /etc/salt/minion
```
Run this command to validate proxy configuration 
```
docker exec -it minion1 more /etc/salt/proxy
```
Run these commands to validate master <-> minion communication
```
docker exec -it master salt minion1 test.ping
docker exec -it master salt "minion1" cmd.run "more /etc/salt/minion"
```
Run these commands to validate master <-> proxies communication
```
docker exec -it master salt -G 'os_family:junos' test.ping
```
Run these commands to validate master <-> proxies <-> junos devices communication
```
docker exec -it master salt -G 'os_family:junos' junos.cli "show version"
```
to watch the event bus, start a shell session on the master and run this command:
```
docker exec -it master bash
salt-run state.event pretty=True
```
## JSNAPy

Run these commands 
``` 
docker exec -it master jsnapy --version
docker exec -it master more /etc/jsnapy/testfiles/test_telnet.yml
```


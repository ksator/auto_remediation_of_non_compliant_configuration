## clone the repository
```
git clone https://github.com/ksator/auto_remediation_of_non_compliant_configuration.git
cd auto_remediation_of_non_compliant_configuration
```

## Update the variables.yml file 

The [variables.yml](https://github.com/ksator/auto_remediation_of_non_compliant_configuration/blob/master/variables.yml) file defines devices ip address, credentials, .... 
```
vi variables.yml
```
## Use the Makefile to start the setup

There is a [Makefile](https://github.com/ksator/auto_remediation_of_non_compliant_configuration/blob/master/Makefile) at the root of the repository 

Run this command to generate SaltStack files, instantiate a docker network and docker containers (Request Tracker, SaltStack master, SaltStack minion), start SaltStack services (master, minion) and daemons (one proxy for each Junos device)   
```
make up
```
Run these commands to verify 
```
docker-compose ps
docker ps
docker images
```
Run this commands to validate master <-> proxies <-> junos devices communication
```
docker exec -it master salt -G 'os_family:junos' junos.cli "show version"
```

## Configure the Junos devices 

Run this command to configure the Junos devices with the host-name and the syslog server indicated in the [variables.yml](https://github.com/ksator/auto_remediation_of_non_compliant_configuration/blob/master/variables.yml) file  

```
docker exec -it master salt -G 'os_family:junos' state.apply syslog
```
Run these command to verify
```
docker exec -it master salt -G 'os_family:junos' junos.cli "show configuration system host-name"
docker exec -it master salt -G 'os_family:junos' junos.cli "show configuration system syslog"
```

## Run the demo


configure telnet on a Junos device
```
$ ssh jcluser@100.123.1.0
Password:
Last login: Sat Mar 30 13:44:53 2019 from 100.123.35.0
--- JUNOS 17.4R1-S2.2 Kernel 64-bit  JNPR-11.0-20180127.fdc8dfc_buil
jcluser@vMX1>

jcluser@vMX1> edit
Entering configuration mode

[edit]
jcluser@vMX1# set system services telnet

[edit]
jcluser@vMX1# commit and-quit
commit complete
Exiting configuration mode
```

SaltStack received the syslog commit message, and runs a JSNAPy test to audit the new Junos configuration.  
Telnet is not allowed. The new Junos configuration is not compliant with the JSNAPy rules. The JSNAPy test fails.  
SaltStack updates the ticketing system (Request Tracker) to report this issue.  

![RT-new-ticket.png](https://github.com/ksator/auto_remediation_of_non_compliant_configuration/blob/master/RT-new-ticket.png)  

Then, SaltStack fixes this issue, and reports this new activity on the ticketing system.   
![RT-ticket-update.png](https://github.com/ksator/auto_remediation_of_non_compliant_configuration/blob/master/RT-ticket-update.png)  

The ticket id is indicated in the Junos commit message.  

```
jcluser@vMX1> show system commit
0   2019-03-30 14:30:31 UTC by jcluser via netconf
    configured with SaltStack using the delete_telnet.xml file to remove telnet configuration due to ticket 1
1   2019-03-30 14:30:19 UTC by jcluser via cli
```
```
jcluser@vMX1> show configuration | compare rollback 1
[edit system services]
-    telnet;
```

**So, in few seconds only, the new issue has been automatically detected, reported, and fixed**  

## Use the Makefile to start a shell session in a container

To start a shell session in a container, run one of these commands:
```
make master-cli
```
```
make minion-cli
```

## Use the Makefile to stop the setup

Run this command to stop docker containers, remove docker containers, remove docker network
```
make down
```
Verify
```
docker-compose ps
docker ps
docker ps -a
docker images
```


jcluser@ubuntu:~$ salt --version
salt 2019.2.0 (Fluorine)

jcluser@ubuntu:~$ jsnapy --version
JSNAPy version: 1.3.2


jcluser@ubuntu:~$ more /etc/jsnapy/testfiles/test_telnet.yml
tests_include:
  - test_telnet_config

test_telnet_config:
  - rpc: get-config
  - kwargs:
      filter_xml: configuration/system
  - item:
      xpath: system/services
      tests:
        - not-exists: telnet
          err: "Test Failed!! telnet is configured"
          info: "Test succeeded!! telnet is not configured"

jcluser@ubuntu:~$


jcluser@ubuntu:~$ more  /srv/runners/jsnapy.py
from jnpr.jsnapy import SnapAdmin
from pprint import pprint
import yaml
import salt.runner
import salt.client

def check_compliance(hostname, test_file):
    opts = salt.config.master_config('/etc/salt/master')
    runner = salt.runner.RunnerClient(opts)
    pillar = runner.cmd('pillar.show_pillar', [hostname])
    config_file_object = {
        "hosts": [
            {
                "device":  pillar['proxy']['host'],
                "username": pillar['proxy']['username'],
                "passwd": pillar['proxy']['passwd']
            }
        ],
        "tests": [
            test_file
        ]
    }
    config_file = yaml.dump(config_file_object)
    js = SnapAdmin()
    snapcheck_output = js.snapcheck(config_file, "automatic_snapshot_from_saltstack")
    json_output = {}
    for item in snapcheck_output:
        json_output = {
            'jsnapy_device_name': hostname,
            'jsnapy_device_ip': item.device,
            'jsnapy_result': item.result,
            'jsnapy_nbr_passed': item.no_passed,
            'jsnapy_nbr_failed': item.no_failed,
            'jsnapy_test_file': test_file
            }
    if json_output['jsnapy_result'] == 'Failed':
        caller = salt.client.LocalClient()
        caller.cmd(hostname, 'event.send', ['jnpr/compliance/failed'], kwarg={'result': json_output})
    return json_output




jcluser@ubuntu:~$ more /srv/runners/request_tracker.py
import rt
import salt.runner
import salt.client

def get_rt_pillars():
    opts = salt.config.master_config('/etc/salt/master')
    runner = salt.runner.RunnerClient(opts)
    pillar = runner.cmd('pillar.show_pillar')
    return(pillar)

def connect_to_rt():
   rt_pillars=get_rt_pillars()
   uri = rt_pillars['rt']['uri']
   username = rt_pillars['rt']['username']
   password = rt_pillars['rt']['password']
   tracker = rt.Rt(uri, username, password)
   tracker.login()
   return tracker

def check_if_a_ticket_already_exist(subject, tracker):
   id=0
   for item in tracker.search(Queue='General'):
       if (item['Subject'] == subject) and (item['Status'] in ['open', 'new']):
           id=str(item['id']).split('/')[-1]
   return id

def create_ticket(subject, text, next_event, device, test_file):
    tracker=connect_to_rt()
    if check_if_a_ticket_already_exist(subject, tracker) == 0:
        ticket_id = tracker.create_ticket(Queue='General', Subject=subject, Text=text)
        json_output = {
            'jsnapy_device_ip': device,
            'jsnapy_test_file': test_file,
            'ticket_id': ticket_id
            }
        caller = salt.client.LocalClient()
        caller.cmd('minion1', 'event.send',['jnpr/enforce_compliancy/start'], kwarg={'result': json_output})
    else:
        ticket_id = check_if_a_ticket_already_exist(subject, tracker)
        tracker.reply(ticket_id, text=text)
        json_output = {
            'jsnapy_device_ip': device,
            'jsnapy_test_file': test_file,
            'ticket_id': ticket_id
            }
        caller = salt.client.LocalClient()
        caller.cmd('minion1' , 'event.send',['jnpr/enforce_compliancy/start'], kwarg={'result': json_output})
    tracker.logout()
    return ticket_id

def update_ticket_with_auto_remediation_activity(ticket_id, text):
    tracker=connect_to_rt()
    tracker.reply(ticket_id, text=text)
    tracker.logout()
    return ticket_id



jcluser@ubuntu:~$ more /etc/salt/master
engines:
    - junos_syslog:
        port: 516
runner_dirs:
    - /srv/runners
pillar_roots:
    base:
        - /srv/pillar
file_roots:
    base:
        - /srv/salt
auto_accept: True





jcluser@ubuntu:~$  more /etc/salt/minion
master: 100.123.35.0
id: minion1




jcluser@ubuntu:~$ more /etc/salt/proxy
master: 100.123.35.0

jcluser@ubuntu:~$ ifconfig eth0
eth0      Link encap:Ethernet  HWaddr 00:50:56:01:23:00
          inet addr:100.123.35.0  Bcast:100.123.255.255  Mask:255.255.0.0
          inet6 addr: fe80::250:56ff:fe01:2300/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:276077 errors:0 dropped:67 overruns:0 frame:0
          TX packets:146169 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:346211385 (346.2 MB)  TX bytes:22870786 (22.8 MB)



jcluser@ubuntu:~$ more /srv/pillar/top.sls
base:
    '*':
        - rt
    'vMX1':
        - vMX1-details
    'vMX2':
        - vMX2-details




jcluser@ubuntu:~$ more /srv/pillar/rt.sls
rt:
    uri: 'http://100.123.35.0:9080/REST/1.0/'
    username: root
    password: password




jcluser@ubuntu:~$ more /srv/pillar/vMX1-details.sls
proxy:
    proxytype: junos
    host: 100.123.1.0
    username: jcluser
    port: 830
    passwd: Juniper!1
syslog_host: 100.123.35.0


jcluser@ubuntu:~$ more /srv/pillar/vMX2-details.sls
proxy:
    proxytype: junos
    host: 100.123.1.1
    username: jcluser
    port: 830
    passwd: Juniper!1
syslog_host: 100.123.35.0



jcluser@ubuntu:~$ more /etc/salt/master.d/reactor.conf
reactor:
    - 'jnpr/syslog/*/UI_COMMIT_COMPLETED':
        - /srv/reactor/check_services_compliancy.sls
    - 'jnpr/compliance/failed':
        - /srv/reactor/create_compliancy_ticket.sls
    - 'jnpr/enforce_compliancy/start':
        - /srv/reactor/enforce_compliancy.sls



jcluser@ubuntu:~$ more /srv/reactor/create_compliancy_ticket.sls
create_a_new_ticket_or_update_the_existing_one:
    runner.request_tracker.create_ticket:
        - args:
            subject: "Device {{ data['data']['result']['jsnapy_device_name'] }} configuration is not inline with the rules described in {{ data['data']['resu
lt']['jsnapy_test_file'] }}"
            text: " {{ data['data']['result'] }}"
            next_event: jnpr/enforce_compliancy/start
            device: "{{ data['data']['result']['jsnapy_device_ip'] }}"
            test_file: "{{ data['data']['result']['jsnapy_test_file'] }}"
jcluser@ubuntu:~$




jcluser@ubuntu:~$  more /srv/reactor/check_services_compliancy.sls
check_telnet:
    runner.jsnapy.check_compliance:
        - args:
            hostname: "{{ data['hostname'] }}"
            test_file: /etc/jsnapy/testfiles/test_telnet.yml




jcluser@ubuntu:~$ more /srv/reactor/enforce_compliancy.sls
enforce_compliancy:
  local.state.apply:
    - tgt: "J@proxy:host:{{ data['data']['result']['jsnapy_device_ip'] }}"
    - tgt_type: compound
    {% if data['data']['result']['jsnapy_test_file'] == '/etc/jsnapy/testfiles/test_telnet.yml' %}
    - arg:
      - delete_telnet
    - kwarg:
        pillar:
          ticket_id: {{ data['data']['result']['ticket_id'] }}
    {% endif %}
    - require:
      - update_ticket_with_auto_remediation_activity

update_ticket_with_auto_remediation_activity:
  runner.request_tracker.update_ticket_with_auto_remediation_activity:
    - args:
        ticket_id: "{{ data['data']['result']['ticket_id'] }}"
        text: saltstack starting auto remediation of non compliant configuration

jcluser@ubuntu:~$



jcluser@ubuntu:~$ more /srv/salt/syslog.sls
configure_syslog:
    junos.install_config:
        - name: salt://syslog.conf
        - timeout: 20
        - replace: False
        - overwrite: False
        - comment: "configured with SaltStack using the model syslog"

jcluser@ubuntu:~$ more /srv/salt/syslog.conf
system {
    syslog {
        host {{ pillar["syslog_host"] }} {
            any any;
            match "UI_COMMIT_COMPLETED";
            port 516;
        }
    }
}


jcluser@ubuntu:~$ more /srv/salt/delete_telnet.
more: stat of /srv/salt/delete_telnet. failed: No such file or directory
jcluser@ubuntu:~$ more /srv/salt/delete_telnet.
delete_telnet.sls  delete_telnet.xml
jcluser@ubuntu:~$ more /srv/salt/delete_telnet.xml
<configuration>
        <system>
            <services>
                <telnet operation="delete">
                </telnet>
            </services>
        </system>
</configuration>

jcluser@ubuntu:~$ more /srv/salt/delete_telnet.sls
delete_telnet:
    junos.install_config:
        - name: salt://delete_telnet.xml
        - timeout: 20
        - replace: False
        - overwrite: False
        - comment: "configured with SaltStack using the delete_telnet.xml file to remove telnet configuration due to ticket {{ pillar['ticket_id'] }}"
jcluser@ubuntu:~$













install docker

docker pull netsandbox/request-tracker
docker run -d --rm --name rt -p 9080:80 netsandbox/request-tracker

pip install requests nose six rt


jcluser@vMX-addr-1# set system host-name vMX2



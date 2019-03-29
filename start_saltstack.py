import os
from yaml import load


os.system('docker exec -it master service salt-master start')
os.system('docker exec -it minion1 service salt-minion start')

f=open('variables.yml', 'r')
devices_list = load(f.read())['junos']
f.close()
for item in devices_list: 
  print 'starting salt proxy for device ' +  item['name'] 
  shell_cmd = 'docker exec -it minion1 salt-proxy -d --proxyid=' + item['name']  
  os.system(shell_cmd)




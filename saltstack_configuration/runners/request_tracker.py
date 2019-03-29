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


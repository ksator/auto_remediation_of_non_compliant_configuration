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

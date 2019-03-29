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


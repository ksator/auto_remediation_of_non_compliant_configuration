create_a_new_ticket_or_update_the_existing_one:
    runner.request_tracker.create_ticket:
        - args:
            subject: "Device {{ data['data']['result']['jsnapy_device_name'] }} configuration is not inline with the rules described in {{ data['data']['result']['jsnapy_test_file'] }}"
            text: " {{ data['data']['result'] }}"
            next_event: jnpr/enforce_compliancy/start
            device: "{{ data['data']['result']['jsnapy_device_ip'] }}"
            test_file: "{{ data['data']['result']['jsnapy_test_file'] }}"


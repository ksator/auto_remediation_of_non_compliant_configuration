check_telnet:
    runner.jsnapy.check_compliance:
        - args:
            hostname: "{{ data['hostname'] }}"
            test_file: /etc/jsnapy/testfiles/test_telnet.yml

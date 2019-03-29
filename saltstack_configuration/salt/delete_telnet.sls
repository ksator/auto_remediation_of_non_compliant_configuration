delete_telnet:
    junos.install_config:
        - name: salt://delete_telnet.xml
        - timeout: 20
        - replace: False
        - overwrite: False
        - comment: "configured with SaltStack using the delete_telnet.xml file to remove telnet configuration due to ticket {{ pillar['ticket_id'] }}"

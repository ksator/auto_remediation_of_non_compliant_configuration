This repository is about **auto remediation** of non compliant configuration  

It uses Junos devices, SaltStack and Jsnapy.  
At each Junos commit, SaltStack is notified with a syslog message, and runs a Jsnapy test to audit the new Junos configuration.  
If the Junos configuration is not compliant with the Jsnapy rules, SaltStack fixes the issue and reports its activities on a ticketing system (Request Tracker)  

Visit [**wiki**](https://github.com/ksator/auto_remediation_of_non_compliant_configuration/wiki) for instructions  



This repository is about **auto remediation** of non compliant configuration  

This repository uses Junos devices, SaltStack, JSNAPy and Request Tracker.  
At each Junos commit, SaltStack is notified with a syslog message, and runs a JSNAPy test to audit the new Junos configuration.  
If the Junos configuration is not compliant with the JSNAPy rules, SaltStack updates the ticketing system (Request Tracker) with this issue, and fixes the issue and reports this activity on the ticketing system.  
The ticket id is indicated in the Junos commit message.  

Visit [**wiki**](https://github.com/ksator/auto_remediation_of_non_compliant_configuration/wiki) for instructions  



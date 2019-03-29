from yaml import load
from jinja2 import Template

################ get the variables value ##############

my_variables_file=open('variables.yml', 'r')
my_variables_in_string=my_variables_file.read()
my_variables_in_yaml=load(my_variables_in_string)
my_variables_file.close()

################# render minion conf file ###################

f=open('saltstack_templates/minion.j2')
my_template = Template(f.read())
f.close()

f=open('saltstack_configuration/minion','w')
f.write(my_template.render(my_variables_in_yaml))
f.close()

################ render proxy config file ###################

f=open('saltstack_templates/proxy.j2')
my_template = Template(f.read())
f.close()

f=open('saltstack_configuration/proxy','w')
f.write(my_template.render(my_variables_in_yaml))
f.close()

################### render pillar files ################################
f=open('saltstack_templates/pillars_top.j2')
my_template = Template(f.read())
f.close()

f=open('saltstack_configuration/pillar/top.sls','w')
f.write(my_template.render(my_variables_in_yaml))
f.close()

f=open('saltstack_templates/rt.j2')
my_template = Template(f.read())
f.close()

f=open('saltstack_configuration/pillar/rt.sls','w')
f.write(my_template.render(my_variables_in_yaml))
f.close()

f=open('saltstack_templates/pillars_device.j2')
my_template = Template(f.read())
f.close()

for item in my_variables_in_yaml['junos']:
    f=open('saltstack_configuration/pillar/' + item['name'] +'-details.sls','w')
    f.write(my_template.render(item))
    f.close()





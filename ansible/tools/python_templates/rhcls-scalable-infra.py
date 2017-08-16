#!/usr/bin/python

import ravello_quick_template as ravello

bastion = ravello.Vm(name="0Bastion Host", tag="bastion", boot_disk_size_GB=40, 
                     ip="10.0.1.10", mac="2c:c2:60:75:d9:20",
                     num_cpus=2, mem_size=2)
bastion.add_hard_drive(name='vol', size=100)
bastion.add_service(name='ssh', external=True, port_range=22, protocol='SSH')
bastion.add_service(name='scp', external=True, port_range=3820, protocol='TCP')

osptokyo = ravello.Vm(name="1OSP all-in-one Tokyo", tag="osptokyo", boot_disk_size_GB=150, 
                     ip="10.2.0.10", mac="2c:c2:60:75:d0:16",
                     num_cpus=4, mem_size=16)
osptokyo.add_service(name='http', external=True, port_range=80, protocol='HTTP')
osptokyo.add_service(name='https', external=True, port_range=443, protocol='HTTPS')
osptokyo.add_service(name='novnc', external=True, port_range=6080, protocol='TCP')

ospparis = ravello.Vm(name="2OSP all-in-one Paris", tag="ospparis", boot_disk_size_GB=150, 
                     ip="10.3.0.10", mac="2c:c2:60:6a:ad:e1",
                     num_cpus=4, mem_size=16)
ospparis.add_service(name='http', external=True, port_range=80, protocol='HTTP')
ospparis.add_service(name='https', external=True, port_range=443, protocol='HTTPS')
ospparis.add_service(name='novnc', external=True, port_range=6080, protocol='TCP')

ospnewyork = ravello.Vm(name="3OSP all-in-one NewYork", tag="ospnewyork", boot_disk_size_GB=150, 
                     ip="10.4.0.10", mac="2c:c2:60:22:52:d7",
                     num_cpus=4, mem_size=16)
ospnewyork.add_service(name='http', external=True, port_range=80, protocol='HTTP')
ospnewyork.add_service(name='https', external=True, port_range=443, protocol='HTTPS')
ospnewyork.add_service(name='novnc', external=True, port_range=6080, protocol='TCP')

cloudforms = ravello.Vm(name="4CloudForms 4.2", tag="cloudforms", boot_disk_size_GB=40, 
                     ip="10.0.1.20", mac="2c:c2:60:7e:44:d3",
                     num_cpus=4, mem_size=16)
cloudforms.add_service(name='http', external=True, port_range=80, protocol='HTTP')
cloudforms.add_service(name='https', external=True, port_range=443, protocol='HTTPS')
cloudforms.add_hard_drive(name='vol', size=60)
cloudforms.add_hard_drive(name='vol2', size=60)

template = ravello.Template(bastion, osptokyo, ospparis,ospnewyork,cloudforms)
print template.to_yaml()

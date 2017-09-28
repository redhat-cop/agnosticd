#!/usr/bin/python

import ravello_quick_template as ravello

bastion = ravello.Vm(name="Bastion Host", tag="bastion", boot_disk_size_GB=10,
                     ip="10.0.1.10", mac="2c:c2:60:14:42:52", services=["ssh"],
                     num_cpus=2, mem_size=2)
bastion.add_hard_drive(HardDrive(name='vol', size=200))

template = ravello.Template(bastion, tokyo, paris, newyork, cloudforms)
print template.to_yaml()

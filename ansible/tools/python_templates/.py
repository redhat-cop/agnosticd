#!/usr/bin/python

import ravello_quick_template as ravello

bastion = ravello.Vm(name="Bastion Host", tag="bastion", boot_disk_size_GB=40, 
                     ip="10.0.1.10", mac="2c:c2:60:14:42:52", services=["ssh"],
                     num_cpus=2, mem_size=2)

www1 = ravello.Vm(name="Web Server", tag="www1", boot_disk_size_GB=40, 
                  ip="10.0.1.20", mac="2c:c2:60:14:42:53", services=["http"],
                  num_cpus=1, mem_size=2)

www2 = ravello.Vm(name="Web Server", tag="www2", boot_disk_size_GB=40, 
                  ip="10.0.1.30", mac="2c:c2:60:14:42:54", services=["http"],
                  num_cpus=1, mem_size=2)

template = ravello.Template(bastion, www1, www2)
print template.to_yaml()

#!/bin/python

import sys
import yaml

DEFAULT_BOOT_IMAGE = "rhel-guest-image-7.3-35.x86_64"
#DEFAULT_BOOT_IMAGE = "Fedora-Workstation-Live-x86_64-26-1.5.iso"

def yaml_indent(level):
    return '  ' * level
# Ensure all required kwargs are present
def kwargs_check(kwargs, key_list, fn_name):
    for x in key_list:
        if x not in kwargs:
            raise Exception("Missing required keyword argument: " + x)
    for y in kwargs:
        if y not in key_list:
            raise Exception("Invalid keyword argument: " + y)

# return kwargs[k] if it exists,
# otherwise return default
def from_kwargs(kwargs, k, default):
    if k in kwargs:
        return kwargs[k]
    elif type(default) is Exception:
        raise default
    else:
      return default

class HardDrive:
    def __init__(self, **kwargs):
        self.name  = from_kwargs(kwargs, 'name', 'vol')
        self.memory_size = from_kwargs(kwargs, 'size', 40)

        self.memory_unit = from_kwargs(kwargs, 'memory_unit', "GB")
        self.bootable = from_kwargs (kwargs, 'bootable', False)
        self.controller = "virtio"
        self.image =  from_kwargs(kwargs, 'image', '')
        self.device_type = from_kwargs(kwargs, 'device_type', "DISK")

class Service:
    def __init__(self, **kwargs):
        self.name = \
            from_kwargs(
                kwargs, 
                'name', 
                Exception('Missing required field: name'))
        self.external = from_kwargs(kwargs, 'external', True)
        self.port_range = \
            from_kwargs(
                kwargs, 
                'port_range', 
                Exception('Missing required field: port_range'))
        self.protocol = \
            from_kwargs(
                kwargs, 
                'protocol', 
                 Exception('Missing required field: protocol'))
        self.ip = \
            from_kwargs(
                kwargs, 
                'ip', 
                Exception('Missing required field: ip'))
       
class NetworkDevice:
    def __init__(self, name, ip, mac):
        self.name = name
        self.controller = "virtio"
        self.ip = ip
        self.ip_public = False
        self.mac = mac
    def gen_ip_yaml(self, base_indent_level):
        b = base_indent_level
        ip_str = "ipConfig:\n" + \
                yaml_indent(b + 1) + \
                 "autoIpConfig:\n" + \
                 yaml_indent(b + 2) + \
                 "reservedIp: " + \
                 self.ip + "\n"
        if self.ip_public:
            ip_str = ip_str + \
                     yaml_indent(b + 1) + \
                     "hasPublicIp: true\n"
        return ip_str
    def gen_mac_yaml(self, base_indent_level):
        b = base_indent_level
        if self.mac == "auto":
            mac_str = "useAutomaticMac: True"
        else:
            mac_str = "useAutomaticMac: False\n" + \
                      yaml_indent(b) + \
                      "mac: " + \
                      self.mac
        return mac_str

class Vm:
    def __init__(self, **kwargs):
        # Parse kwargs
        self.name = kwargs['name']
        self.tag = kwargs['tag']
        self.description = \
           from_kwargs(
               kwargs, 
               'description', 
               "\"" + self.name + "\\nnohbac: true\\n\"")

        self.num_cpus = from_kwargs(kwargs, 'num_cpus', 1)
        self.memory_size = from_kwargs(kwargs, 'mem_size', 2)
        self.memory_unit = from_kwargs(kwargs, 'memory_unit', "GB")

        self.hostnames = \
            from_kwargs(kwargs, 'hostnames',
            [self.tag + "-REPL.rhpds.opentlc.com",
            self.tag + ".example.com",
            self.tag])

        self.hard_drives = []
        self.network_devices = []
        self.stop_timeout = 300
        self.ip = kwargs['ip']
        self.mac = from_kwargs(kwargs, 'mac', 'auto')
        self.services = []
        self.users = []

        # Add boot disk
        boot_hd = \
            HardDrive(
                name=from_kwargs(kwargs, 'hd_name', 'root disk'), 
                image=from_kwargs(kwargs, 'boot_image', DEFAULT_BOOT_IMAGE),
                size=kwargs['boot_disk_size_GB'])
        boot_hd.bootable = True
        self.hard_drives.append(boot_hd)

        # Add network devices

        eth0_ip = self.ip
        eth0 = NetworkDevice("eth0", eth0_ip, self.mac)
        eth0.ip_public = True
        self.network_devices.append(eth0)
        
    def add_hard_drive(self, **kwargs):
        hd = HardDrive(**kwargs)
        self.hard_drives.append(hd)

    def add_service(self, **kwargs):
        kwargs['ip'] = from_kwargs(kwargs, 'ip', self.ip)
        s = Service(**kwargs)
        self.services.append(s)

    def vm_core_yaml(self):
        core_yaml = """\
- name: {vm_name}
  tag: {vm_tag}
  description: {vm_description}
  numCpus: {vm_num_cpus}
  memorySize:
    unit: {vm_memory_unit}
    value: {vm_memory_size}
  hostnames: {vm_hostnames_list}
  supportsCloudInit: True
  keypairId: 62226455
  keypairName: "opentlc-admin-backdoor"
  userData: |
    #cloud-config
    ssh_pwauth: False
    disable_root: False
    users:
      - name: "{{{{ remote_user }}}}"
        sudo: ALL=(ALL) NOPASSWD:ALL
        lock_passwd: False
        ssh-authorized-keys:
          - "{{{{ env_public_key }}}}"
    runcmd:
      - sed -i -e '/^GSSAPIAuthentication/s/^.*$/GSSAPIAuthentication no/' /etc/ssh/sshd_config
      - sed -i -e '$aUseDNS no' /etc/ssh/sshd_config
      - systemctl restart sshd
"""
        return core_yaml.format(
            vm_name = self.name, 
            vm_tag = self.tag, 
            vm_description = self.description,
            vm_num_cpus = self.num_cpus,
            vm_memory_unit = self.memory_unit,
            vm_memory_size = self.memory_size,
            vm_hostnames_list = \
                yaml.dump(self.hostnames).rstrip())

    def vm_hard_drives_yaml(self):
        def convert_hd_yaml(hd, index):
            hd_yaml = """\
  - index: {hd_index}{hd_image_str}
    boot: {hd_boot}
    controller: {hd_controller}
    name: {hd_name}
    size:
      unit: {hd_memory_unit}
      value: {hd_memory_size}
    type: {hd_type}
"""
            return hd_yaml.format(
               hd_index = index,
               hd_image_str = \
               (lambda: '' \
                 if hd.image == '' \
                 else '\n    imageName: ' + hd.image)(),
               hd_boot = hd.bootable,
               hd_controller = hd.controller,
               hd_name = hd.name,
               hd_memory_unit = hd.memory_unit,
               hd_memory_size = hd.memory_size,
               hd_type = hd.device_type)

        hard_drives_yaml = "".join([convert_hd_yaml(hd, i) \
                  for i, hd in enumerate(self.hard_drives)])
        return "  hardDrives:\n" + hard_drives_yaml

    def vm_network_devices_yaml(self):
        def convert_nd_yaml(nd, index):
            nd_yaml = """\
  - name: {nd_name}
    device:
      index: {nd_index}
      deviceType: {nd_controller}
      {nd_mac_section}
    {nd_ip_section}"""
            return nd_yaml.format(
                nd_name = nd.name,
                nd_index = index,
                nd_controller = nd.controller,
                nd_mac_section = nd.gen_mac_yaml(3),
                nd_ip_section = nd.gen_ip_yaml(2))
        network_device_yaml = "".join([convert_nd_yaml(nd, i) \
                 for i, nd in enumerate(self.network_devices)])
        return "  networkConnections:\n" + network_device_yaml

    def vm_services_yaml(self):
        services_yaml = "  suppliedServices:\n"
        for service in self.services:
            yaml_segment = """\
  - external: {service_external}
    ip: {service_ip}
    name: {service_name}
    portRange: {service_portrange}
    protocol: {service_protocol}
"""
            services_yaml = \
                services_yaml + \
                    yaml_segment.format(
                        vm_ip = self.ip, 
                        service_external = service.external,
                        service_name = service.name,
                        service_protocol = service.protocol,
                        service_portrange = service.port_range,
                        service_ip = service.ip)
        return services_yaml

    def to_yaml(self):
      return "".join([self.vm_core_yaml(), 
                      self.vm_hard_drives_yaml(), 
                      self.vm_network_devices_yaml(),
                      self.vm_services_yaml()])
class Template:
    def __init__(self, *args):
        self.vm_list =  args
    def add_vm(self, vm):
        self.vm_list.append(vm)
    def to_yaml(self):
        vm_list_yaml = "".join([vm.to_yaml() \
              for i, vm in enumerate(self.vm_list)])
        return "vms:\n" + vm_list_yaml
        

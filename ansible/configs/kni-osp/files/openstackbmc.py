#!/usr/bin/env python
__author__ = 'alberto.gonzalez@redhat.com'

import argparse
import logging
import pyghmi.ipmi.bmc as bmc
import pyghmi.ipmi.command as ipmicommand
import signal
import sys
import threading
import time
from pprint import pprint

import openstack

#IPMI_PORT = 623

global my_bmc
global my_thread
global my_lock

def start_bmc(args, ipmi_password, api_password, ipmi_port):
    global my_bmc
    global my_lock

    my_lock = threading.Lock()
    my_lock.acquire()

    my_bmc = OpenStackBmc({'admin': ipmi_password},
                        port=int(ipmi_port),
                        address=args.address,
                        auth_url=args.auth_url,
                        username=args.api_username,
                        password=api_password,
                        project_name=args.project_name,
                        vm_name=args.vm_name,
                        pxe_image=args.pxe_image)

    if not my_bmc.connect():
        my_lock.release()
        msg = "Failed to connect to API server. Exiting"
        logging.error(msg)
        print(msg)
        sys.exit(1)

    # We must release the lock here to avoid a dead lock since
    # bmc.listen() is a busy loop
    my_lock.release()

    my_bmc.listen()


class OpenStackBmc(bmc.Bmc):
    """OpenStack IPMI virtual BMC."""

    def get_vm(self, name):
        """Get a VM by name."""
        vms = self._client.compute.servers()
        for vm in vms:
            if vm.name == name:
                return vm

        msg = 'vm not found: {0}'.format(name)
        logging.error(msg)
        raise ValueError(msg)

    def connect(self):
        """Connect to the OpenStack API server with the given credentials."""
        try:
            self._client = openstack.connect(
                auth=dict(
                auth_url=self._auth_url,
                project_name=self._project_name,
                username=self._username,
                password=self._password,
                project_domain_name="Default",
                user_domain_name="Default"),
                identity_api_version=3,
                region_name="regionOne",
            )

            return True
        except Exception as e:
            msg = "Exception while connecting to API server:" + str(e)
            logging.error(msg)
            print(msg)
            return False

    def __init__(self, authdata, port, address, auth_url , username, password,
                 project_name, vm_name, pxe_image):
        """OpenStack virtual BMC constructor."""
        self._client = None
        super(OpenStackBmc, self).__init__(authdata,
                                         address=address,
                                         port=port)
        self._auth_url = auth_url
        self._username = username
        self._password = password
        self._project_name = project_name
        self._vm_name = vm_name
        self._pxe_image = pxe_image
        self._boot_order_changed = False
        self._server_unrescued = False

    def disconnect(self):
        """Disconnect from the OpenStack API server."""
        if not self._client:
            return

        self._client.close()

    def __del__(self):
        """OpenStack virtual BMC destructor."""
        self.disconnect()

    # Disable default BMC server implementations

    def cold_reset(self):
        """Cold reset reset the BMC so it's not implemented."""
        raise NotImplementedError

    def get_boot_device(self):
        """Get the boot device of a OpenStack VM."""

        self._vm = self.get_vm(self._vm_name)
        metadata = self._client.compute.get_server_metadata(self._vm)
        return 0x04

    def set_boot_device(self, bootdevice):
        self._vm = self.get_vm(self._vm_name)
        logging.info('set boot device ' + bootdevice + ' for vm ' + self._vm_name + ' with status ' + self._vm.status)
        metadata = self._client.compute.get_server_metadata(self._vm)
        current = ""
        if "bootorder" in metadata.metadata:
          current = metadata.metadata["bootorder"]
        if current != bootdevice:
          if bootdevice in ("hd"):
            if self._vm.status == "RESCUE":
              self._client.compute.unrescue_server(self._vm)
              self._server_unrescued = True
          self._boot_order_changed = bootdevice
        return True

    def set_kg(self, kg):
        """Desactivated IPMI call."""
        raise NotImplementedError

    def power_reset(self):
        """Reset a VM."""
        # Shmulik wrote "Currently, limited to: "chassis power on/off/status"
        raise NotImplementedError

    # Implement power state BMC features
    def get_power_state(self):
        """Get the power state of a OpenStack VM."""
        try:
            self._vm = self.get_vm(self._vm_name)

            if self._vm.status in ['STARTED','ACTIVE','BUILDING', 'RESCUE']:
                if self._vm.status == "ACTIVE" and self._server_unrescued:
                  self._client.compute.stop_server(self._vm)
                  self._server_unrescued = False
                  return "off"
                logging.info('returning power state ON for vm ' + self._vm_name)
                return "on"
            else:
                if self._boot_order_changed:
                  logging.info('boot order changed for vm ' + self._vm_name + ' to ' + self._boot_order_changed)
                  self._client.compute.set_server_metadata(self._vm,bootorder=self._boot_order_changed)
                  metadata = self._client.compute.get_server_metadata(self._vm)
                  if self._boot_order_changed == "network":
                    logging.info('autostart (rescue) ' + self._vm_name + ' using' + self._boot_order_changed)
                    self._client.compute.rescue_server(self._vm,image_ref=self._pxe_image)
                  else:
                    logging.info('autostart (unrescue) ' + self._vm_name + ' using ' + self._boot_order_changed)
                    try:
                      self._client.compute.unrescue_server(self._vm)
                    except:
                      pass
                    self._client.compute.start_server( self._vm)
                  self._boot_order_changed = False
                logging.info('returning power state OFF for vm ' + self._vm_name)
                return "off"

        except Exception as e:
            logging.error(self._vm_name + ' get_power_state:' + str(e))
            return 0xc0

        return "off"

    def power_off(self):
        """Cut the power without waiting for clean shutdown."""
        self._vm = self.get_vm( self._vm_name)
        logging.info("Power OFF called for VM " + self._vm_name + " with state: " + self._vm.status)
        if self._vm.status in ['STARTED','ACTIVE']:
          try:
              self._client.compute.stop_server( self._vm)
          except Exception as e:
              logging.error(self._vm_name + ' power_off:' + str(e))
              return 0xc0
        elif self._vm.status in ['RESCUE']:
          try:
              self._client.compute.unrescue_server(self._vm)
              self._server_unrescued = True
              #self._client.compute.reset_server_state(self._vm,"active")
              #self._client.compute.stop_server( self._vm)
          except Exception as e:
              logging.error(self._vm_name + ' power_off:' + str(e))
              return 0xc0
        elif self._vm.status in ['SHUTOFF']:
          return False
        else:
          return 0xc0

    def power_on(self):
        """Start a vm."""
        self._vm = self.get_vm( self._vm_name)
        metadata = self._client.compute.get_server_metadata(self._vm)
        logging.info("Power ON called for VM " + self._vm_name + " with state: " + self._vm.status)
        if self._vm.status == 'SHUTOFF':
          try:
              current = ""
              if "bootorder" in metadata.metadata:
                 current = metadata.metadata["bootorder"]
              if current == "network":
                self._client.compute.rescue_server(self._vm,image_ref=self._pxe_image)
              else:
                self._client.compute.start_server( self._vm)
          except Exception as e:
              logging.error(self._vm_name + ' power_on:' + str(e))
              return 0xc0
        else:
          return False

    def power_shutdown(self):
        """Gently power off while waiting for clean shutdown."""
        logging.info("Power SHUTDOWN called for VM " + self._vm_name + " with state: " + self._vm.status)
        self._vm = self.get_vm( self._vm_name)
        if self._vm.status == 'STARTED':
          try:
              self._client.compute.stop_server( self._vm)
          except Exception as e:
              logging.error(self._vm_name + ' power_shutdown:' + str(e))
              return 0xc0
        else:
          return 0xc0

def parse_args():
    parser = argparse.ArgumentParser(
        prog='openstackbmc',
        description='The OpenStack virtual BMC',
    )

    # Use a compact format for declaring command line options
    arg_list = []
    arg_list.append(['address', 'Address to listen on; defaults to localhost'])
    arg_list.append(['auth-url', 'Auth url'])
    arg_list.append(['api-username', 'User name '])
    arg_list.append(['project-name', 'Name of the OSP project'])
    arg_list.append(['vm-name', 'Name of the VMX virtual machine'])
    arg_list.append(['ipmi-password', 'IPMI Password'])
    arg_list.append(['ipmi-port', 'IPMI Port'])
    arg_list.append(['api-password', 'API Password'])
    arg_list.append(['pxe-image', 'PXE image'])

    # expand the list of command line options
    for arg in arg_list:
        parser.add_argument('--%s' % arg[0],
                            dest=arg[0].replace('-', '_'),
                            type=str,
                            help=arg[1],
                            required=True)

    parser.add_argument('--debug',
                        dest='debug',
                        action='store_true',
                        help='Enable OpenStack SDK debugging')

    return parser.parse_args()


def exit_signal(signal, frame):
    global my_bmc
    global my_thread
    global my_lock
    my_thread._Thread__stop()
    my_thread.join()

    my_lock.acquire()
    my_bmc.disconnect()
    my_lock.release()

    sys.exit(0)

if __name__ == '__main__':
    args = parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    ipmi_password = args.ipmi_password

    api_password = args.api_password

    ipmi_port = args.ipmi_port


    global my_thread
    my_thread = threading.Thread(target=start_bmc,
                                 args=(args, ipmi_password, api_password, ipmi_port))
    my_thread.start()

    signal.signal(signal.SIGINT,  exit_signal)

    while True:
        time.sleep(1)

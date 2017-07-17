# env-access-tool-generator

Generates access tools for unique individual cloud suite environments.  


### Description

The purpose of this tool is to provide a uniform interface to access all
cloud suite demo environment sessions.  This is accomplished by generating
a custom script for each environment, based on the user's username and the 
environment's guid.  

Each generated script provides an abstracted command line interface to 
ssh connections, including bash sessions and log monitoring, to various
machines used in the Red Hat Cloud Suite Demos.   It also provides organized 
URL resolution of the browser-based Cloud Suite administration panels and 
the online tutorial documents. 

The generated `<guid>-access` scripts contain all of the information they will
need to establish connections.  This helps avoid the necessity of typing environment 
URLs over and over.

### Generator Tool Details

```env-access-tool-generator -u <username> -g <environment-guid> -k <ssh-private-key-path>```

If the username or guid flags are not provided, the user will be prompted for 
the missing paramaters interactively.  If the ssh key is not provided, it will be
set to the default value of ```~/.ssh/id_rsa```.

The tool will then generate a ```<guid>-access``` script which can be used to easily 
access a Cloud Suite Demo environment.

### Access Tool Details

Each `<guid>-access` script takes a series of arguments corresponding to the 
environment type and desired connection to establish.

```
<guid>-access <environment-type <options>:
    flags: -acc <options>  | --accelerating-service-delivery <options>
              options: ssh <server>
                           demo # ssh to the demo server
                           cf   # ssh to the cloudforms server
                           satellite  # ssh to the satellite server
                       monitor <server-log>
                               cf-automation-log # ssh to cloudforms server and 
                                             monitor automation.log
                               forman-production-log   # ssh to satellite and 
                                                         monitor foreman production log
                       gui # opens the admin panels in a browser
                       end-web-page # opens the finished webpage in a browser
                       guide # opens the accelerating service delivery demo guide

           -opt <options>  | --optimize-it <options>
              options: ssh <server>
                           demo # ssh to the demo server
                           cf   # ssh to the cloudforms server
                       monitor <server-log>
                               cf-automation-log     # ssh to cloudforms server and 
                                                 monitor automation.log
                               cf-migration-logs # ssh to cloudforms server and 
                                                 monitor migration logs
                               cf-migration-errs # ssh to cloudforms server and 
                                                 monitor migration errs
                       gui   # opens the admin panels in a browser
                       guide # opens the optimize i.t. demo guide in a browser

           -mod <options>  | --modernize-devops <options>
              options: ssh <server>
                           workstation # ssh to the workstation server
                           ocp-master  # shh to the openstack master server
                       gui     # opens the admin panels in a browser
                       console # opens the web openstack console frontend in a browser
                       guide   # opens the modernizing devops demo guide in a browser

           -scal <options> | --scalable-infrastructure <options>
              options: gui     # opens the admin panels in a browser
                       guide   # opens the scalable infrastructure demo 
                                 guide in a browser
           -qci <options>  | --quick-cloud-installer
              options: ssh <server> 
                           workstation # ssh to the workstation server
                           undercloud  # ssh to the undercloud server
                       gui     # opens the opentlc admin panel in a browser
                       guide   # opens the quick start cloud installer demo guide
                       
           -h | --help # print help

```

### Example Use Case - Accelerating Service Delivery 

The following is a brief example of how the Generator and Access Tools can be used.  The access tools have equivalent and expanded functionality for each other demo.

In this scenario, the demo environment has been provisioned and is finished building.  
The user has updated their ssh keys, and the associated private key is located at 
```~/.ssh/id_rsa```.

The user first generates a  `<guid>-access` tool using:

```env-access-tool-generator -u <username> -g <environment-guid> -k <ssh-private-key-path>```


To access the Accelerating Service Delivery guide in a web browser:

```
$ <guid>-access -acc guide
```

The first step in the [2. Getting Started](https://www.opentlc.com/demo-guides/Lab_redhat-cloud-suite-deployment-demo.html#_getting_started) section is to set up the ssh connections to cloudforms and satellite to monitor the automation log and the foreman production log.  This can be accomplished with the following commands:

```
\# In one terminal
$ ./<guid>-access -acc cf-automation-log

\# In another terminal
$ ./<guid>-access -acc foreman-production-log
```

Next, the user can access bring up all graphical administration panels by executing:
```
$ ./<guid>-access -acc gui
```

The user's complete interface to the environment should now be open, and the demo can be run.  Once the demo is finished, the user can run the following command to access the verification web page:
```
$ ./<guid>-access -acc end-web-page
```

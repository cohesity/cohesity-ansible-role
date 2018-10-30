# Guide to configuring your Ansible Inventory

## SYNOPSIS
The Cohesity.Ansible role includes several Demo and Complete plays designed to help you get your feet wet with using Ansible to manage your Cohesity cluster.  As part of this solution, we have integrated heavily with the Ansible Inventory to help streamline the process.  The inventory is a collection of hosts and variables that controls how the connections can be made.  We are able to leverage this information to simplify the process of deploying an entire solution on Day 1.

## Ansible Inventory File

### What is it?
> Ansible works against multiple systems in your infrastructure at the same time. It does this by selecting portions of systems listed in Ansible’s inventory, which defaults to being saved in the location /etc/ansible/hosts. You can specify a different inventory file using the -i <path> option on the command line.

[More details on the Ansible Inventory File](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)

### Special Note about Windows Hosts
By default, Ansible leverages Python and SSH to communicate.  This role is written specifically to be used from a Linux based workstation and leveraging Python.  However, the module `cohesity_win_agent` is the exception to this rule.  This module will allow for the installation of the Cohesity Agent on Physical Windows servers by means with WinRM and Powershell.  In order to connect, please read the Official documentation on [Setting up a Windows Host](https://docs.ansible.com/ansible/latest/user_guide/windows_setup.html) to work with Ansible.

### Required Components
The Below list comprises the required settings and values in order to leverage the demo and complete examples.

| Key Name | Description | Usage |
| --- | --- | --- |
| **[workstation]** | Required: Single host identifier from which calls to the Cohesity Cluster will be made.  This can be your local machine or a remote Linux workstation.  | If local, leverage the `ansible_connection=local` option to prevent SSH calls |
| [physical:children] | Collection of groups to include in all Physical Environment actions | This can be a collection of other groups like<br>[physical:children]<br>linux<br>windows |
| [group_name] | Organized by Platform, OS, or any other common characteristics.  The name of the server should be resolvable otherwise insert `ansible_host=IP` to handle the registration.|  If each item should have different values, then each of the supported inventory options can be included there. |
| [group_name:vars] | Collection of variables belonging to the specific named group.  This can include any defauls required such as authentication settings or other related variables. | Note: If specific configured in the [group_name] a variable at that level will override the value in this section. |
| [vmware] | Inventory name followed by **ansible_host**="vCenter IP" information for managed VMware Endpoints | Note: If the inventory name is resolvable, then the `ansible_host` information is not required. |
| [vmware:vars] | Supported Variables as required by VMware Environment Management | Variable Types:<br>**type**=VMware<br>**vmware_type**=VCenter<br>**source_username**=username<br>**source_password**=password|
| [generic_nas] | Inventory name followed by **endpoint**="path" information for managed GenericNas Endpoints | Note: Windows Shares must have each '\' escaped as such `\\\\windows_host\\share_name` |
| [generic_nas:vars] | Supported Variables as required by GenericNas Environment Management | Variable Types:<br>**type**=GenericNas<br>**nas_protocol**=SMB<br>**nas_username**=username<br>**nas_password**=password|

### Example Ansible Inventory File
```
# => Workstation Declaration which will also be included in our
# => Backup
[workstation]
control ansible_connection=local ansible_host=10.2.x.x type=Linux

[centos]
centos6 ansible_host=10.2.x.x
centos7 ansible_host=10.2.x.x

# => Default variables for all CentOS environments
[centos:vars]
type=Linux
ansible_user=root
ansible_become=False

# => Grouping of all Linux hosts
[linux:children]
centos
workstation

# Physical Windows Servers
[windows]
windows12 ansible_host=10.2.x.x
windows16 ansible_host=10.2.x.x

# => Windows Variables to leverage for each Windows Server.
[windows:vars]
type=Windows
install_type=volcbt
reboot_after_install=True
ansible_user=administrator
ansible_password=password
ansible_port=5986
ansible_connection=winrm
ansible_winrm_server_cert_validation=ignore

# => Group all Physical Servers.  This grouping is used by the Demos and Complete
# => Examples to identify Physical Servers
[physical:children]
linux
windows

# => Declare the VMware environments to manage.
[vmware]
vcenter01 ansible_host=10.2.x.x

[vmware:vars]
type=VMware
vmware_type=VCenter
source_username=administrator
source_password=password

# => Declare the GenericNas endpoints to manage
[generic_nas]
export_path endpoint="10.2.x.x:/export_path" nas_protocol=NFS
nas_share endpoint="\\\\10.2.x.x\\nas_share"
data endpoint="\\\\10.2.x.x\\data"

# => Default variables for GenericNas endpoints.
[generic_nas:vars]
type=GenericNas
nas_protocol=SMB
nas_username=.\cohesity
nas_password=password
```

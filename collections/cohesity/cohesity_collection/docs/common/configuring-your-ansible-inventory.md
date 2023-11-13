# Configure Your Ansible Inventory

[Go back to Documentation home page ](../README.md)

## Table of Contents
- [Synopsis](#synopsis)
- [Ansible Inventory File](#Ansible-Inventory-File)
    - [What is it?](#What-is-it)
    - [Special Note about Windows Hosts](#Special-Note-about-Windows-Hosts)
    - [Required Components](#Required-Components)
    - [Example Ansible Inventory File](#Example-Ansible-Inventory-File)

## Synopsis
[top](#Configure-Your-Ansible-Inventory)

The Cohesity Ansible Role includes several Demo and Complete plays designed to help you get started using Ansible to manage your Cohesity cluster.  As part of this solution, we have integrated heavily with the Ansible Inventory to help streamline the process.  The inventory is a collection of hosts and variables that controls how the connections are made.  We are able to leverage this information to simplify the process of deploying an entire solution on Day 1.

## Ansible Inventory File
[top](#Configure-Your-Ansible-Inventory)

### What is it?
[top](#Configure-Your-Ansible-Inventory)

> Ansible works against multiple systems in your infrastructure at the same time. It does this by selecting portions of systems listed in Ansible’s inventory, which defaults to being saved in the `/etc/ansible/hosts` location. You can specify a different inventory file using the *-i <path>* option on the command line.

For more details on the Ansible Inventory File, see [Working with Inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) in the *Ansible User Guide*.

### Special Note about Windows Hosts
[top](#Configure-Your-Ansible-Inventory)

By default, Ansible uses Python and SSH to communicate.  This role is written specifically to be used from a Linux-based workstation, leveraging Python.  However, the `cohesity_win_agent` module is the exception to this.  That module allows you to install the Cohesity Agent on Physical Windows servers by using WinRM and Powershell.  To connect and work with Ansible, read [Setting up a Windows Host](https://docs.ansible.com/ansible/latest/user_guide/windows_setup.html).

### Required Components
[top](#Configure-Your-Ansible-Inventory)

The list below comprises the required settings and values in order to use the Demo and Complete examples.

| Key Name | Description | Usage |
| --- | --- | --- |
| **[workstation]** | Required: Single host identifier from which calls to the Cohesity cluster are made.  This can be your local machine or a remote Linux workstation.  | If local, employ the `ansible_connection=local` option to prevent SSH calls. |
| [physical:children] | Collection of groups to include in all Physical Environment actions | This can be a collection of other groups like<br>[physical:children]<br>linux<br>windows |
| [group_name] | Organized by platform, OS, or any other common characteristics.  If the name of the server does not resolve, insert `ansible_host=IP` to handle the registration.|  If each item should have different values, then each of the supported inventory options can be included there. |
| [group_name:vars] | Collection of variables belonging to the named group.  This can include any required defaults, such as authentication settings or other related variables. | **Note**: If specifically configured in `[group_name]`, a variable at that level will override the value in this section. |
| [vmware] | Inventory name followed by **ansible_host**="vCenter IP" information for managed VMware endpoints | **Note**: If the inventory name is resolvable, then the `ansible_host` information is not required. |
| [vmware:vars] | Supported variables as required by VMware Environment Management | Variable Types:<br>**type**=VMware<br>**vmware_type**=VCenter<br>**source_username**=username<br>**source_password**=password|
| [generic_nas] | Inventory name followed by **endpoint**="path" information for managed GenericNas Endpoints | **Note**: Windows Shares must have '\' escaped, as in: `\\\\windows_host\\share_name` |
| [generic_nas:vars] | Supported variables as required by GenericNas Environment Management | Variable Types:<br>**type**=GenericNas<br>**nas_protocol**=SMB<br>**nas_username**=username<br>**nas_password**=password|

### Example Ansible Inventory File
[top](#Configure-Your-Ansible-Inventoryy)

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

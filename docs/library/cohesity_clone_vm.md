# Cohesity Clone Management 

[Go back to Documentation home page ](../README.md)

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Syntax](#syntax)
- [Examples](#examples)
  - [Create a VMware VM clone](#Create-a-VMware-VM-clone)
  - [Destroy a VMware VM clone](#Destroy-a-VMware-VM-clone)
- [Parameters](#parameters)
- [Outputs](#outputs)

## Synopsis
[top](#cohesity-clone-management)

The Ansible Module is used to clone VMs using snapshots of backup made from VMs.

### Requirements
[top](#cohesity-clone-management)

* Cohesity DataPlatform running version 6.3 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher
* [Python Management SDK](https://developer.cohesity.com/apidocs-641.html#/python/getting-started)

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - When using the default download location, the Cohesity agent installer is placed in `/tmp/<temp-dir`.  If your environment prevents the use of `/tmp` with a `noexec` option, then you must set an alternate location.

## Syntax
[top](#cohesity-clone-management)

```yaml
- cohesity_clone_vm:
    name: <Name of the Clone Task>
    state: <Determines if the Clone Task should be present or absent from in Cohesity Cluster>
    job_name: <Protection Group/Job name from where VM will be cloned>
    view_name: <Specifies the name of the View where the cloned VMs are stored.>
    backup_timestamp: <Specify point in time snapshot using this option. The formart should be YYYY-MM-DD:hh:mm. If not selected, the most recent backup is used>
    environment: <Specify the source environment type. Default is VMware >
    vm_names: <List of the VMs that will be cloned>
    wait_for_job: <Wait for clone task to finish, waits for wait minutes passed to module, default wait minutes is 30 mins>
    prefix: <Add prefix to cloned VM name >
    suffix: <Add suffix to cloned VM name >
    power_on: <Specify if you want cloned VM powered on or off>
    network_conntected: <Specifies whether the network should be left in disabled state. Attached network is enabled by default. Set this flag to true to disable it>
    wait_minutes: <Wait time in minutes, time to wait for clone task>
    resource_pool: <Specifies the resource pool where the cloned VMs are attached.> 
```

## Examples
[top](#cohesity-clone-management)

### Create a VMware VM clone
[top](#cohesity-clone-management)

```yaml
- cohesity_clone_vm:
    cluster: cohesity.lab
    username: admin
    password: password
    name: CLONE_TASK_NAME
    job_name: JOB_NAME
    view_name: VIEW_NAME
    environment: VMware
    vm_names:
        - VM_Name1
        - VM_Name2
    resource_pool: RESOURCE_POOL_NAME
    state: present
```

### Destroy a VMware VM clone
[top](#cohesity-clone-management)

```yaml
- cohesity_clone_vm:
    cluster: cohesity.lab
    username: admin
    password: password
    name: CLONE_TASK_NAME
    job_name: JOB_NAME
    view_name: VIEW_NAME
    environment: VMware
    vm_names:
        - VM_Name1
        - VM_Name2
    resource_pool: RESOURCE_POOL_NAME
    state: absent
```

## Parameters
[top](#cohesity-clone-management)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity cluster |
| X | **username** | String | | Username with which Ansible will connect to the Cohesity cluster (username used to login to cluster from UI). Domain-specific credentials can be configured .<br>- Domain@username|
| X | **password** | String | | Password belonging to the selected Username (password used to login to cluster from UI).  This parameter is not logged. |
| X | **name** | String | | Name of the Cloned VM. |
|  | state | Choice | -**present**<br>-absent | Determines if the clone should be present or absent from the host.|
| X | **job_name** | String | | Protection Group/Job name from where VM will be cloned. |
| X | **view_name** | String | | Specifies the name of the View where the cloned VMs are stored. |
| | backup_timestamp | String | | Specify point in time snapshot using this option. The formart should be YYYY-MM-DD:hh:mm. If not selected, the most recent backup is used |
| | environment | Choice | VMware | Select the source environment for cloning. |
|   | vm_names | List | | List of the VMs that will be cloned. |
|   | wait_for_job | Boolean | True | Wait for clone task to finish, waits for wait minutes passed to module, default wait minutes is 30 mins|
|  | prefix | String | | Add prefix to cloned VM name. |
|  | suffix |String | | Add suffix to cloned VM name. |
|   | power_on | Boolean | True | Specify if you want cloned VM powered on or off.|
|   | network_connected | Boolean | True | Specifies whether the network should be left in disabled state. Attached network is enabled by default. Set this flag to true to disable it|
|   | wait_minutes | Integer | 30 | Wait time in minutes, time to wait for clone task|
| X | **resource_pool** | String | | Specifies the resource pool where the cloned VMs are attached. |


## Outputs
[top](#cohesity-clone-management)
- N/A


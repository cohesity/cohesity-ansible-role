# Cohesity Clone Management 

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

The Ansible Module creates, modifies or deletes a Protection Policy for the Cohesity Cluster

### Requirements
[top](#cohesity-clone-management)

* Cohesity DataPlatform running version 6.3 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - When using the default download location, the Cohesity agent installer is placed in `/tmp/<temp-dir`.  If your environment prevents the use of `/tmp` with a `noexec` option, then you must set an alternate location.

## Syntax
[top](#cohesity-clone-management)

```yaml
- cohesity_clone_vm:
    name: <Name of the Clone Task>
    state: <Determines if the Clone Task should be present or absent from the host>
    job_name: <Protection Group/Job name from where VM will be cloned>
    view_name: <View name which will be cloned along with the VM>
    backup_timestamp: <Specify point in time snapshot using this option>
    environment: <Specify point in time snapshot using this option>
    vm_name: <Name of the VMs that will be cloned>
    wait_for_job: <Specify whether you want for the clone job to finish before proceeding>
    prefix: <Add prefix to cloned VM name >
    suffix: <Add suffix to cloned VM name >
    power_on: <Specify if you want cloned VM powered on or off>
    network_conntected: <Specify if you want cloned VM connected to network or a detached network>
    wait_minutes: <Specify wait time in mins>
    resource_pool: <Detail of the destination where VM will be cloned to> 
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
| X | **name** | String | | Name of the Cloned VM. |
|  | state | Choice | -**present**<br>-absent | Determines if the clone should be present or absent from the host.|
| X | **job_name** | String | | Protection Group/Job name from where VM will be cloned. |
| X | **view_name** | String | | View name which will be cloned along with the VM. |
| | backup_timestamp | String | | Specify point in time snapshot using this option. |
| | environment | Choice | VMware | Select the source environment for cloning. |
|   | vm_names | List | | Name of the VMs that will be cloned. |
|   | wait_for_job | Boolean | True | Specify whether you want for the clone job to finish before proceeding|
|  | prefix | String | | Add prefix to cloned VM name. |
|  | suffix |String | | Add suffix to cloned VM name. |
|   | power_on | Boolean | True | Specify if you want cloned VM powered on or off.|
|   | network_connected | Boolean | True | Specify if you want cloned VM powered on or off.|
|   | wait_minutes | Integer | 30 | Specify wait time in mins|
| X | **resource_pool** | String | | Detail of the destination where VM will be cloned to |


## Outputs
[top](#cohesity-clone-management)
- N/A


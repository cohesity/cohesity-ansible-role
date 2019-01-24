# Cohesity Restore Virtual Machines

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Syntax](#syntax)
- [Examples](#examples)
  - [Restore a single Virtual Machine](#Restore-a-single-Virtual-Machine)
  - [Restore multiple Virtual Machines from a specific snapshot with a new prefix and disable the network](#Restore-multiple-Virtual-Machines-from-a-specific-snapshot-with-a-new-prefix-and-disable-the-network)
- [Parameters](#parameters)
- [Outputs](#outputs)

## Synopsis
[top](#cohesity-restore-virtual-machines)

This Ansible Module supports Physical and GenericNAS environments and initiates a file and folder recovery operation for the chosen Cohesity Protection Job on a Cohesity cluster.  When executed in a playbook, the Cohesity Restore operation is validated and the appropriate recovery action is applied.

### Requirements
[top](#cohesity-restore-virtual-machines)

* Cohesity DataPlatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Note:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.

## Syntax
[top](#cohesity-restore-virtual-machines)

```yaml
- cohesity_restore_file:
    server: <ip or hostname for cohesity cluster>
    cohesity_admin: <username with cluster level permissions>
    cohesity_password: <password for the selected user>
    validate_certs: <boolean to determine if SSL certificates should be validated>
    state: <state of the Recovery Operation>
    name: <assigned descriptor to assign to the Recovery Job.  The Recovery Job name will consist of the job_name:name format>
    environment: <protection source environment type>
    job_name: <selected Protection Job from which the recovery will be initated>
    endpoint: <identifies the source endpoint to which the the recovery operation will be performed>
    backup_id: <optional Cohesity Backup Run ID for the restore operation.  If not selected, the most recent RunId will be used>
    backup_timestamp: <not implemented>
    vm_names:
      - <list of virtual machines to be recovered by the operation>
    wait_for_job: <boolean to determine if the task should wait for the recovery operation to complete prior to moving to the next operation>
    wait_minutes: <number of minutes to wait until the job completes>
    datastore_id: <id of the datastore to which the machines will be restored>
    datastore_folder_id: <id of the datastore_folder to which the machines will be restored>
    network_connected: <boolean to determine if the virtual machine network should be connected>
    network_id: <id of the network to which the virtual machines should be connected>
    power_state: <boolean to determine if the restored machines should be powered on>
    resource_pool_id: <id of the resource pool to which the virtual machines will be restored>
    prefix: <string prepended to the begining of the virtual machine name>
    suffix: <string appended to the end of the virtual machine name>
    vm_folder_id: <id of the vCenter Folder to which the machine will be restored>
```

## Examples
[top](#cohesity-restore-virtual-machines)


### Restore a single Virtual Machine
[top](#cohesity-restore-virtual-machines)

```yaml
- name: Restore a Virtual Machine
  cohesity_restore_vm:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    name: "Ansible Test VM Restore"
    endpoint: "myvcenter.cohesity.demo"
    environment: "VMware"
    job_name: "myvcenter.cohesity.demo"
    vm_names:
      - chs-win-01
```

### Restore multiple Virtual Machines from a specific snapshot with a new prefix and disable the network
[top](#cohesity-restore-virtual-machines)

```yaml
- name: Restore a Virtual Machine
  cohesity_restore_vm:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    name: "Ansible Test VM Restore"
    endpoint: "myvcenter.cohesity.demo"
    environment: "VMware"
    job_name: "myvcenter.cohesity.demo"
    backup_id: "48291"
    vm_names:
      - chs-win-01
      - chs-win-02
    prefix: "rst-"
    network_connected: no

```

## Parameters
[top](#cohesity-restore-virtual-machines)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity cluster |
| X | **cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity cluster. Domain-specific credentails can be configured in one of two formats.<br>- Domain\\username<br>- username@domain |
| X | **cohesity_password** | String | | Password belonging to the selected Username.  This parameter is not logged. |
|   | validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |
|   | state | Choice | -**present**<br>-absent<br>-started<br>-stopped | Determines the state of the Recovery Operation. |
| X | **name** | String | | Descriptor to assign to the Recovery Job.  The Recovery Job name will consist of the job_name:name format |
| X | **job_name** | String | | Name of the Protection Job |
| X | **environment** | Choice | -VMware | Specifies the environment type (such as VMware) of the Protection Source this Job is protecting. Supported environment types include 'VMware' |
| X | **endpoint** | String | | Specifies the network endpoint where the Protection Source is reachable. It can be the URL, hostname, IP address, NFS mount point, or SMB Share of the Protection Source. |
|   | backup_id | String |  | Optional Cohesity ID to use as source for the Restore operation.  If not selected, the most recent RunId will be used. |
|   | backup_timestamp | String |  | Not implemented. |
| X | **vm_names** | Array |  | Array of Virtual Machines to restore. |
|   | wait_for_job | Boolean | True | Should wait until the Restore Job completes |
|   | wait_minutes | String | 5 | Number of minutes to wait until the job completes. |
|   | datastore_id | String | | Specifies the datastore where the object’s files should be recovered to. This field is mandatory to recover objects to a different resource pool or to a different parent source. If not specified, objects are recovered to their original datastore locations in the parent source. |
|   | datastore_folder_id | String | | Specifies the folder where the restore datastore should be created. This is applicable only when the VMs are being cloned. |
|   | network_connected | Boolean | True | Specifies whether the network should be left in disabled state. Attached network is enabled by default. Set this flag to true to disable it. |
|   | network_id | String | | Specifies a network configuration to be attached to the cloned or recovered object. Specify this field to override the preserved network configuration or to attach a new network configuration to the cloned or recovered objects. You can get the networkId of the kNetwork object by setting includeNetworks to ‘true’ in the GET /public/protectionSources operation. In the response, get the id of the desired kNetwork object, the resource pool, and the registered parent Protection Source. |
|   | power_state | Boolean | True| Specifies the power state of the cloned or recovered objects. By default, the cloned or recovered objects are powered off. |
|   | resource_pool_id | String | | Specifies the resource pool where the cloned or recovered objects are attached. |
|   | prefix | String | | Specifies a prefix to prepended to the source object name to derive a new name for the recovered or cloned object. |
|   | suffix | String | | Specifies a suffix to appended to the original source object name to derive a new name for the recovered or cloned object |
|   | vm_folder_id | String | | Specifies a folder where the VMs should be restored |


## Outputs
[top](#cohesity-restore-virtual-machines)

- Returns the Recovery Operation Details as an array of Recovery Job details.

```json
{
    "changed": true, 
    "msg": "Registration of Cohesity Restore Job Complete", 
    "name": "myvcenter.cohesity.demo Ansible Test VM Restore", 
    "restore_jobs": [
        {
            "continueOnError": true, 
            "fullViewName": "cohesity_int_54879", 
            "id": 54879, 
            "newParentId": 1, 
            "objects": [
                {
                    "jobRunId": 48291, 
                    "jobUid": {
                        "clusterId": 8621173906188849, 
                        "clusterIncarnationId": 1538852526333, 
                        "id": 46969
                    }, 
                    "protectionSourceId": 1049, 
                    "startedTimeUsecs": 1547151172462136
                }
            ], 
            "poweredOn": false, 
            "prefix": "rst-", 
            "startTimeUsecs": 1548083898761275, 
            "status": "Finished", 
            "targetViewCreated": true, 
            "type": "kRecoverVMs", 
            "username": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER", 
            "viewBoxId": 5, 
            "vm_names": [
                "chs-win-01"
            ], 
            "vmwareParameters": {}
        }
    ]
}
```
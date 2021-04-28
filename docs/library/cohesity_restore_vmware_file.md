# Cohesity Restore VMware Files

[Go back to Documentation home page ](../README.md)

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Syntax](#syntax)
- [Examples](#examples)
  - [Restore a single file from a VMware VM Backup](#Restore-a-single-file-from-a-VMware-VM-Backup)
  - [Restore multiple files from a specific VMware Backup and wait for up to 10 minutes for the process to complete](#Restore-multiple-files-from-a-specific-VMware-Backup-and-wait-for-up-to-10-minutes-for-the-process-to-complete)
- [Parameters](#parameters)
- [Outputs](#outputs)

## Synopsis
[top](#cohesity-restore-vmware-files)

This Ansible Module supports VMware environment and initiates a file and folder restore operation for the chosen Cohesity Protection Job on a Cohesity cluster.  When executed in a playbook, the Cohesity restore operation is validated and the appropriate restore action is applied.

### Requirements
[top](#cohesity-restore-vmware-files)

* Cohesity DataPlatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Note:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.

## Syntax
[top](#cohesity-restore-vmware-files)

```yaml
- cohesity_restore_vmware_file:
    cluster: <ip or hostname for cohesity cluster>
    username: <cohesity username with cluster level permissions>
    password: <cohesity password for the selected user>
    validate_certs: <boolean to determine if SSL certificates should be validated>
    state: <state of the restore operation>
    name: <assigned descriptor to assign to the Restore Job.  The Restore Job name will consist of the job_name:name format>
    job_name: <selected Protection Job from which the restore will be initated>
    endpoint: <identifies the source endpoint to which the the restore operation will be performed>
    backup_timestamp: <optional Cohesity Backup Run time. The formart should be YYYY-MM-DD:hh:mm. If not selected, the most recent backup is used>
    file_names:
      - <list of files and folders to be restored by the operation>
    wait_for_job: <boolean to determine if the task should wait for the restore operation to complete prior to moving to the next operation>
    wait_minutes: <number of minutes to wait until the job completes>
    overwrite: <boolean to determine if the restore operation should overwrite the files or folders if they exist>
    preserve_attributes: <boolean to determine if the restore operation should maintain the original file or folder attributes>
    restore_location: <optional location to which the files will be restored>
```

## Examples
[top](#cohesity-restore-vmware-files)

### Restore multiple files from a specific VMware Backup and wait for up to 10 minutes for the process to complete
[top](#cohesity-restore-vmware-files)

```yaml
- cohesity_restore_vmware_file:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    name: Restore Single File
    job_name: myhost
    endpoint: myvcenter.host.lab
    file_names:
      - C:\\data\\files
      - C:\\data\\large_directory
    vm_name: "demo"
    vm_username: admin
    vm_password: admin
    wait_for_job: yes
    wait_minutes: 10
```

### Restore a single file from a VMware VM Backup
[top](#cohesity-restore-vmware-files)

```yaml
---
- cohesity_restore_vmware_file:
    name: "Ansible File Restore to Virtual Machine"
    job_name: "myvm.demo"
    endpoint: "myvcenter.cohesity.demo"
    files:
      - "/home/cohesity/sample"
    wait_for_job: True
    state: "present"
    backup_timestamp: 2021-04-11:21:37
    restore_location: /home/cohesity/
    vm_name: "demo"
    vm_username: admin
    vm_password: admin

```


## Parameters
[top](#cohesity-restore-vmware-files)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity cluster |
| X | **username** | String | | Username with which Ansible will connect to the Cohesity cluster (username used to login to cluster from UI). Domain-specific credentials can be configured as.<br>- username@domain or domain/username (will be deprecated in future).|
| X | **password** | String | | Password belonging to the selected Username (password used to login to cluster from UI).  This parameter is not logged. |
|   | validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |
|   | state | Choice | -**present**<br>-absent<br>-started<br>-stopped | Determines the state of the restore operation. |
| X | **name** | String | | Descriptor to assign to the Restore Job.  The Restore Job name will appear in the format: `job_name:name`. |
| X | **job_name** | String | | Name of the Protection Job |
| X | **endpoint** | String | | Specifies the Vcenter name where file/folder is located.|
| X | **file_names** | Array |  | Array of files and folders to restore |
|   | wait_for_job | Boolean | True | Wait until the Restore Job completes |
|   | wait_minutes | String | 5 | Number of minutes to wait until the job completes. |
|   | overwrite | Boolean | True | If `true`, the restore operation overwrites any existing files or folders. |
|   | preserve_attributes | Boolean | False | If `true`, the restore operation maintains the original file or folder attributes |
|   | restore_location | String |  | Alternate location to which the files will be restored |
|   | backup_timestamp | String |  | Backup Run time for the restore operation. It should be given in YYYY-MM-DD:hh:mm format. If not specified, most recent backup job run is used.
| X | **vm_name** | String | | Name of the VM where files are located. |
| X | **vm_username** | String | | Username of the VM to which the files will be restored. |
| X | **vm_password** | String | | Password of the VM to which the files will be restored. |


## Outputs
[top](#cohesity-restore-vmware-files)

- Returns the restore operation details as an array of Restore Job details.

```json
{
    "changed": true, 
    "failed": false, 
    "filenames": [
        "C:/data/files"
    ], 
    "msg": "Registration of Cohesity Restore Job Complete", 
    "name": "myvcenter: Ansible Test Multi-File Restore", 
    "restore_jobs": [
        {
            "fullViewName": "cohesity_int_54295", 
            "id": 54295, 
            "objects": [
                {
                    "jobRunId": 46979, 
                    "jobUid": {
                        "clusterId": 8621173906188849, 
                        "clusterIncarnationId": 1538852526333, 
                        "id": 46967
                    }, 
                    "protectionSourceId": 1044, 
                    "startedTimeUsecs": 1546967910807987
                }
            ], 
            "startTimeUsecs": 1548001636579142, 
            "status": "Finished", 
            "type": "kRestoreFiles", 
            "username": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER", 
            "viewBoxId": 5
        }
    ]
}
```

# Cohesity Restore Files

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Syntax](#syntax)
- [Examples](#examples)
  - [Restore a single file from a Physical Windows Backup](#Restore-a-single-file-from-a-Physical-Windows-Backup)
  - [Restore a single file from a GenericNas NFS Backup and wait for the job to complete](#Restore-a-single-file-from-a-GenericNas-NFS-Backup-and-wait-for-the-job-to-complete)
  - [Restore multiple files from a specific Physical Windows Backup and wait for up to 10 minutes for the process to complete](#Restore-multiple-files-from-a-specific-Physical-Windows-Backup-and-wait-for-up-to-10-minutes-for-the-process-to-complete)
- [Parameters](#parameters)
- [Outputs](#outputs)

## Synopsis
[top](#cohesity-restore-files)

This Ansible Module supports Physical and GenericNAS environments and initiates a file and folder restore operation for the chosen Cohesity Protection Job on a Cohesity cluster.  When executed in a playbook, the Cohesity restore operation is validated and the appropriate restore action is applied.

### Requirements
[top](#cohesity-restore-files)

* Cohesity DataPlatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Note:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.

## Syntax
[top](#cohesity-restore-files)

```yaml
- cohesity_restore_file:
    cluster: <ip or hostname for cohesity cluster>
    cohesity_admin: <username with cluster level permissions>
    cohesity_password: <password for the selected user>
    validate_certs: <boolean to determine if SSL certificates should be validated>
    state: <state of the restore operation>
    name: <assigned descriptor to assign to the Restore Job.  The Restore Job name will consist of the job_name:name format>
    environment: <protection source environment type. For Physical sources the value is "PhysicalFiles" >
    job_name: <selected Protection Job from which the restore will be initated>
    endpoint: <identifies the source endpoint to which the the restore operation will be performed>
    backup_id: <optional Cohesity Backup Run ID for the restore operation.  If not selected, the most recent RunId will be used>
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
[top](#cohesity-restore-files)

### Restore a single file from a Physical Windows Backup
[top](#cohesity-restore-files)

```yaml
- cohesity_restore_file:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    name: Restore Single File
    job_name: myhost
    environment: PhysicalFiles
    endpoint: mywindows.host.lab
    file_names:
      - C:/data/big_file
    wait_for_job: no
```

### Restore a single file from a GenericNas NFS Backup and wait for the job to complete
[top](#cohesity-restore-files)

```yaml
- cohesity_restore_file:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    name: Restore Single File to NFS Location
    job_name: mynfs
    environment: GenericNas
    endpoint: mynfs.host.lab:/exports
    file_names:
      - /data
    restore_location: /restore
    wait_for_job: yes
```

### Restore multiple files from a specific Physical Windows Backup and wait for up to 10 minutes for the process to complete
[top](#cohesity-restore-files)

```yaml
- cohesity_restore_file:
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
    name: Restore Single File
    job_name: myhost
    environment: PhysicalFiles
    endpoint: mywindows.host.lab
    file_names:
      - C:/data/files
      - C:/data/large_directory
    wait_for_job: yes
    wait_minutes: 10
```

## Parameters
[top](#cohesity-restore-files)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity cluster |
| X | **cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity cluster. Domain-specific credentails can be configured in one of two formats.<br>- Domain\\username<br>- username@domain |
| X | **cohesity_password** | String | | Password belonging to the selected Username.  This parameter is not logged. |
|   | validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |
|   | state | Choice | -**present**<br>-absent<br>-started<br>-stopped | Determines the state of the restore operation. |
| X | **name** | String | | Descriptor to assign to the Restore Job.  The Restore Job name will appear in the format: `job_name:name`. |
| X | **job_name** | String | | Name of the Protection Job |
| X | **environment** | Choice | -PhysicalFiles<br>-GenericNas | Specifies the environment type (such as VMware or MS SQL) of the Protection Source this Job is protecting. For Physical protection source, the value is 'PhysicalFiles' |
| X | **endpoint** | String | | Specifies the network endpoint where the Protection Source is reachable. It can be the URL, hostname, IP address, NFS mount point, or SMB Share of the Protection Source. |
|   | backup_id | String |  | Optional Cohesity ID to use as source for the restore operation.  If not selected, the most recent `RunId` will be used. |
| X | **file_names** | Array |  | Array of files and folders to restore |
|   | wait_for_job | Boolean | True | Wait until the Restore Job completes |
|   | wait_minutes | String | 5 | Number of minutes to wait until the job completes. |
|   | overwrite | Boolean | True | If `true`, the restore operation overwrites any existing files or folders. |
|   | preserve_attributes | Boolean | False | If `true`, the restore operation maintains the original file or folder attributes |
|   | restore_location | String |  | Alternate location to which the files will be restored |
|   | backup_timestamp | String |  | Backup Run time for the restore operation. It should be given in YYYY:MM:DD:hh:mm formart.


## Outputs
[top](#cohesity-restore-files)

- Returns the restore operation details as an array of Restore Job details.

```json
{
    "changed": true, 
    "failed": false, 
    "filenames": [
        "C:/data/files"
    ], 
    "msg": "Registration of Cohesity Restore Job Complete", 
    "name": "mywindows: Ansible Test Multi-File Restore", 
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

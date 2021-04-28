# Task: Cohesity File Restore Operation

[Go back to Documentation home page ](../README.md)

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Ansible Variables](#Ansible-Variables)
- [Customize Your Playbooks](#Customize-your-playbooks)
  - [Restore a File from most recent snapshot](#Restore-a-File-from-most-recent-snapshot)
- [How the Task Works](#How-the-Task-works)

## Synopsis
[top](#task-cohesity-file-restore-operation)

Use this task to perform a Cohesity file restore operation.

#### How It Works
- This Ansible task starts by determining whether the named restore task exists and is not running.
- Upon validation, the task creates a new restore operation to recover files from the cluster.

### Requirements
[top](#task-cohesity-file-restore-operation)

* Cohesity DataPlatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Before using this task, refer to the [Setup](../common/setup.md) and [How to Use](../common/how-to-use.md) sections of this guide.

## Ansible Variables
[top](#task-cohesity-file-restore-operation)

The following is a list of variables and the configuration expected when leveraging this task in your playbook.  For more information on these variables, see [Syntax](../library/cohesity_restore_vmware_file.md) in the Cohesity Restore Files module.
```yaml
cohesity_restore_vmware_file:
  state: "present"
  name: ""
  job_name: ""
  endpoint: ""
  files: ""
  wait_for_job: True
  wait_minutes: 10
  overwrite: True
  preserve_attributes: True
  restore_location: ""
  backup_timestamp: ""
  vm_name: ""
  vm_username: ""
  vm_password: ""
```
## Customize Your Playbooks
[top](#task-cohesity-file-restore-operation)

This example shows how to include the Cohesity Ansible Role in your custom playbooks and leverage this task as part of the delivery.

### Restore a file from most recent snapshot
[top](#task-cohesity-file-restore-operation)

This is an example playbook that creates a new file restore operation for a Protection Job. (Remember to change it to suit your environment.)
> **Notes:**
  - Before using these example playbooks, refer to the [Setup](../common/setup.md) and [How to Use](../common/how-to-use.md) sections of this guide.
  - This example requires that the endpoint matches an existing Protection Source. See the [Cohesity Protection Source Management](../tasks/source.md) task.
  - This example requires that the Protection job exists and has been run at least once. See the [Cohesity Protection Job Management](../tasks/job.md) task.

You can create a file called `restore_files.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> restore_files.yml -e "username=admin password=admin"
  ```

```yaml
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
      - name: Restore Files
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: restore_file
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: False
            cohesity_restore_file:
                name: "Ansible File Restore"
                job_name: "Protect file from Vmware Backup"
                endpoint: "myvcenter.cohesity.demo"
                files:
                  - "/home/cohesity/sample"
                wait_for_job: True
                state: "present"
                backup_timestamp: 2021-04-11:21:37
                restore_location: /home/cohesity/
                vm_name: "TestSdk"
                vm_username: "{{ vm_username }}"
                vm_password: "{{ vm_password }}"

```


## How the Task Works
[top](#task-cohesity-file-restore-operation)

The following information is copied directly from the included task in this role. The source file is located at the root of this role in `/tasks/restore_file.yml`.
```yaml
---
- name: "Cohesity Recovery Job: Restore a set of files"
  cohesity_restore_vmware_file:
    cluster: "{{ cohesity_server }}"
    username: "{{ cohesity_admin }}"
    password: "{{ cohesity_password }}"
    validate_certs: "{{ cohesity_validate_certs | default(False) }}"
    state: "{{ cohesity_restore_file.state | default('present') }}"
    name: "{{ cohesity_restore_file.name | default('') }}"
    job_name: "{{ cohesity_restore_file.job_name | default('') }}"
    endpoint: "{{ cohesity_restore_file.endpoint | default('') }}"
    file_names: "{{ cohesity_restore_file.files | default('') }}"
    wait_for_job: "{{ cohesity_restore_file.wait_for_job | default('yes') }}"
    wait_minutes: "{{ cohesity_restore_file.wait_minutes | default(10) }}"
    overwrite: "{{ cohesity_restore_file.overwrite | default('yes') }}"
    preserve_attributes: "{{ cohesity_restore_file.preserve_attributes | default('yes') }}"
    restore_location: "{{ cohesity_restore_file.restore_location | default('') }}"
    backup_timestamp: "{{ cohesity_restore_file.backup_timestamp | default('') }}"
    vm_name: "{{ cohesity_restore_file.vm_name | default('') }}"
    vm_password: "{{ cohesity_restore_file.vm_password | default('') }}"
    vm_username: "{{ cohesity_restore_file.vm_username | default('') }}"
  tags: always

```

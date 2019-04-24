# Task: Cohesity File Restore Operation

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
  - Before using this task, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

## Ansible Variables
[top](#task-cohesity-file-restore-operation)

The following is a list of variables and the configuration expected when leveraging this task in your playbook.  For more information on these variables, see [Syntax](/modules/cohesity_restore_file.md?id=syntax) in the Cohesity Restore Files module.
```yaml
cohesity_restore_file:
  state: "present"
  name: ""
  environment: "PhysicalFiles"
  job_name: ""
  endpoint: ""
  backup_id: ""
  files: ""
  wait_for_job: True
  wait_minutes: 10
  overwrite: True
  preserve_attributes: True
  restore_location: ""
  backup_timestamp: ""
```
## Customize Your Playbooks
[top](#task-cohesity-file-restore-operation)

This example shows how to include the Cohesity Ansible Role in your custom playbooks and leverage this task as part of the delivery.

### Restore a file from most recent snapshot
[top](#task-cohesity-file-restore-operation)

This is an example playbook that creates a new file restore operation for a Protection Job. (Remember to change it to suit your environment.)
> **Notes:**
  - Before using these example playbooks, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.
  - This example requires that the endpoint matches an existing Protection Source. See the [Cohesity Protection Source Management](tasks/source.md) task.
  - This example requires that the Protection job exists and has been run at least once. See the [Cohesity Protection Job Management](tasks/job.md) task.

You can create a file called `restore_files.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> restore_files.yml -e "username=admin password=admin"
  ```

```yaml
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: "{{ username }}"
        var_cohesity_password: "{{ password }}"
        var_validate_certs: False
        var_cohesity_restore_name: "Ansible Test File Restore"
        var_cohesity_endpoint: 10.2.132.141
        var_cohesity_job_name: "protect_physical_linux"
        var_cohesity_files:
           - "/home/cohesity/Documents"
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
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_restore_file:
                name: "{{ var_cohesity_restore_name }}"
                endpoint: "{{ var_cohesity_endpoint }}"
                environment: "PhysicalFiles"
                job_name: "{{ var_cohesity_job_name }}"
                files: "{{ var_cohesity_files }}"
                wait_for_job: True

```


## How the Task Works
[top](#task-cohesity-file-restore-operation)

The following information is copied directly from the included task in this role. The source file is located at the root of this role in `/tasks/restore_file.yml`.
```yaml
---
- name: "Cohesity Recovery Job: Restore a set of files"
  cohesity_restore_file:
    cluster: "{{ cohesity_server }}"
    username: "{{ cohesity_admin }}"
    password: "{{ cohesity_password }}"
    validate_certs: "{{ cohesity_validate_certs }}"
    state:  "{{ cohesity_restore_file.state | default('present') }}"
    name: "{{ cohesity_restore_file.name | default('') }}"
    environment: "{{ cohesity_restore_file.environment | default('PhysicalFiles') }}"
    job_name: "{{ cohesity_restore_file.job_name | default('') }}"
    endpoint: "{{ cohesity_restore_file.endpoint | default('') }}"
    backup_id: "{{ cohesity_restore_file.backup_id | default('') }}"
    file_names: "{{ cohesity_restore_file.files | default('') }}"
    wait_for_job: "{{ cohesity_restore_file.wait_for_job | default('yes') }}"
    wait_minutes: "{{ cohesity_restore_file.wait_minutes | default(10) }}"
    overwrite: "{{ cohesity_restore_file.overwrite | default('yes') }}"
    preserve_attributes: "{{ cohesity_restore_file.preserve_attributes | default('yes') }}"
    restore_location: "{{ cohesity_restore_file.restore_location | default('') }}"
    backup_timestamp: "{{cohesity_restore_file.backup_timestamp | default('') }}"
  tags: always

```

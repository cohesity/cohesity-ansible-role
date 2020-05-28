# Task: Cohesity Virtual Machine Restore Operation

[Go back to Documentation home page ](../README.md)

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Ansible Variables](#Ansible-Variables)
- [Customize Your Playbooks](#Customize-your-playbooks)
  - [Restore a Virtual Machine from most recent snapshot](#Restore-a-Virtual-Machine-from-most-recent-snapshot)
- [How the Task Works](#How-the-Task-works)

## Synopsis
[top](#task-cohesity-virtual-machine-restore-operation)

Use this task to perform a Cohesity VM restore operation.

#### How It Works
- This Ansible task starts by determining whether the named restore task exists and is not running.
- Upon validation, the task creates a new restore operation to recover VMs from the cluster.

### Requirements
[top](#task-cohesity-virtual-machine-restore-operation)

* Cohesity DataPlatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Before using this task, refer to the [Setup](../common/setup.md) and [How to Use](../common/how-to-use.md) sections of this guide.

## Ansible Variables
[top](#task-cohesity-virtual-machine-restore-operation)

The following is a list of variables and the configuration expected when leveraging this task in your playbook.  For more information on these variables, see [Syntax](../library/cohesity_restore_vm.md) in the Cohesity Restore VM module.
```yaml
cohesity_restore_vm:
  state: present
  name: ""
  environment: VMware
  job_name: ""
  endpoint: ""
  backup_id: ""
  vms: ""
  wait_for_job: ""
  wait_minutes: 0
  datastore_id: ""
  datastore_folder_id: ""
  network_connected: yes
  network_id: ""
  power_state: yes
  resource_pool_id: ""
  prefix: ""
  suffix: ""
  vm_folder_id: ""
```
## Customize Your Playbooks
[top](#task-cohesity-virtual-machine-restore-operation)

This example shows how to include the Cohesity Ansible Role in your custom playbooks and leverage this task as part of the delivery.

### Restore a Virtual Machine from most recent snapshot
[top](#task-cohesity-virtual-machine-restore-operation)

This is an example playbook that creates a new Virtual Machine restore operation for a Protection Job. (Remember to change it to suit your environment.)
> **Notes:**
  - Before using these example playbooks, refer to the [Setup](../common/setup.md) and [How to Use](../common/how-to-use.md) sections of this guide.
  - This example requires that the endpoint matches an existing Protection Source. See the [Cohesity Protection Source Management](../tasks/source.md) task.
  - This example requires that the Protection job exists and has been run at least once. See the [Cohesity Protection Job Management](../tasks/job.md) task.

```yaml
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: admin
        var_cohesity_password: admin
        var_validate_certs: False
        var_cohesity_restore_name: "Ansible Test VM Restore"
        var_cohesity_endpoint:
        var_cohesity_job_name:
        var_cohesity_vms:
        var_power_state: off
        var_network_connected: off
        var_prefix: "rss-"
        var_wait_minutes: 30
        var_wait_for_job: yes
    roles:
      - cohesity.cohesity_ansible_role
    tasks:
      - name: Restore VM
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: restore_vm
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_restore_vm:
                name: "{{ var_cohesity_restore_name }}"
                endpoint: "{{ var_cohesity_endpoint }}"
                environment: "VMware"
                job_name: "{{ var_cohesity_job_name }}"
                vms: "{{ var_cohesity_vms }}"
                power_state: "{{ var_power_state }}"
                network_connected: "{{ var_network_connected }}"
                prefix: "{{ var_prefix }}"
                wait_minutes: "{{ var_wait_minutes }}"
                wait_for_job: "{{ var_wait_for_job }}"

```


## How the Task Works
[top](#task-cohesity-virtual-machine-restore-operation)

The following information is copied directly from the included task in this role. The source file is located at the root of this role in `/tasks/restore_vm.yml`.
```yaml
---
- name: "Cohesity Recovery Job: Restore a set of Virtual Machines"
  cohesity_restore_vm:
    cluster: "{{ cohesity_server }}"
    username: "{{ cohesity_admin }}"
    password: "{{ cohesity_password }}"
    validate_certs: "{{ cohesity_validate_certs }}"
    state:  "{{ cohesity_restore_vm.state | default('present') }}"
    name: "{{ cohesity_restore_vm.name | default('') }}"
    environment: "{{ cohesity_restore_vm.environment | default('Physical') }}"
    job_name: "{{ cohesity_restore_vm.job_name | default('') }}"
    endpoint: "{{ cohesity_restore_vm.endpoint | default('') }}"
    backup_id: "{{ cohesity_restore_vm.backup_id | default('') }}"
    vm_names: "{{ cohesity_restore_vm.vms | default('') }}"
    wait_for_job: "{{ cohesity_restore_vm.wait_for_job | default('yes') }}"
    wait_minutes: "{{ cohesity_restore_vm.wait_minutes | default(30) }}"
    datastore_id: "{{ cohesity_restore_vm.datastore_id | default('') }}"
    datastore_folder_id: "{{ cohesity_restore_vm.datastore_folder_id | default('') }}"
    network_connected: "{{ cohesity_restore_vm.network_connected | default('yes') }}"
    network_id: "{{ cohesity_restore_vm.network_id | default('') }}"
    power_state: "{{ cohesity_restore_vm.power_state | default('yes') }}"
    resource_pool_id: "{{ cohesity_restore_vm.resource_pool_id | default('') }}"
    prefix: "{{ cohesity_restore_vm.prefix | default('') }}"
    suffix: "{{ cohesity_restore_vm.suffix | default('') }}"
    vm_folder_id: "{{ cohesity_restore_vm.vm_folder_id | default('') }}"
  tags: always

```

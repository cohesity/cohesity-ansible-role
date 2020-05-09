# Task: Cohesity Clone VM 

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Ansible Variables](#Ansible-Variables)
- [Customize Your Playbooks](#Customize-your-playbooks)
  - [Create a VMware VM clone](#Create-a-VMware-VM-clone)
  - [Destroy a VMware VM clone](#Destroy-a-VMware-VM-clone)
- [How the Task Works](#How-the-Task-works)

## Synopsis
[top](#task-Cohesity-clone-vm)

Create and destroy the clone using this task. This is used to create VMs using stored snapshots and perform some dev/test testing.

#### How It Works
- The tasks collects all the information (required and optional) and starts a clone task (if *state=present*).
- The task can also destory a clone (*state=absent*) that was cloned using VMWare workflow.


### Requirements
[top](#task-Cohesity-clone-vm)

* Cohesity DataPlatform running version 6.3 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Before using this task, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

## Ansible Variables
[top](#task-Cohesity-clone-vm)

The following is a list of variables and the configuration expected when using this task in your playbook.  For more information on these variables, see [Cohesity Clone VM](../modules/cohesity_clone.md?id=syntax).
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

## Customize Your Playbooks
[top](#task-Cohesity-clone-vm)

These examples show how to include the Cohesity Ansible Role in your custom playbooks and leverage this task as part of the delivery.

Following inventory file can be used for the ansible-playbook runs below. Copy the content to `inventory.ini` file
```ini
[workstation]
127.0.0.1 ansible_connection=local

[cohesity]
10.21.143.240
```

### Create a VMware VM clone
[top](#task-Cohesity-clone-vm)

This is an example playbook that creates a Clone VM job using the VMWare workflow on the `Cohesity` hosts. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

You can create a file called `cohesity-clone.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> cohesity-clone.yml -e "username=abc password=abc"
  ```

```yaml
---
  - hosts: cohesity
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: "{{ username }}"
        var_cohesity_password: "{{ password }}"
        var_validate_certs: False
    become: true
    roles:
        - cohesity.cohesity_ansible_role
    tasks:
      - name: Create a Clone VM task using VMWare Workflow
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: clone_vm
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_clone_vm:
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
[top](#task-Cohesity-clone-vm)

This is an example playbook that destroys the clone VM task and deletes the VM on all `cohesity` hosts. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

```yaml
---
  - hosts: linux
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: "{{ username }}"
        var_cohesity_password: "{{ password }}"
        var_validate_certs: False
    become: true
    roles:
        - cohesity.cohesity_ansible_role
    tasks:
      - name: Destroy a Clone VM task using VMWare Workflow
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: clone_vm
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
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

## How the Task Works
[top](#task-Cohesity-clone-vm)

The following information is copied directly from the included task in this role.  The source file is located at the root of this role in `/tasks/clone_vm.yml`.
```yaml
---
- name: "Cohesity clone VMs: Set {{ cohesity_clone_vm.name | default('clone_task_name') }} to state of {{ cohesity_clone_vm.state | default('present') }}"
  cohesity_clone_vm:
    cluster: "{{ cohesity_server }}"
    username: "{{ cohesity_admin }}"
    password: "{{ cohesity_password }}"
    validate_certs: "{{ cohesity_validate_certs | default(False) }}"
    state: "{{ cohesity_clone_vm.state | default('present') }}"
    name: "{{ cohesity_clone_vm.name }}"
    environment: "{{ cohesity_clone_vm.environment | default('VMware') }}"
    job_name: "{{ cohesity_clone_vm.job_name }}"
    view_name: "{{ cohesity_clone_vm.view_name }}"
    backup_timestamp: "{{ cohesity_clone_vm.backup_timestamp | default('') }}"
    vm_names: "{{ cohesity_clone_vm.vm_names }}"
    wait_for_job: "{{ cohesity_clone_vm.wait_for_job | default(True) }}"
    wait_minutes: "{{ cohesity_clone_vm.wait_minutes | default(30) }}"
    network_connected: "{{ cohesity_clone_vm.network_connected | default(True) }}"
    power_on: "{{ cohesity_clone_vm.power_on | default(True) }}"
    resource_pool: "{{ cohesity_clone_vm.resource_pool }}"
    prefix: "{{ cohesity_clone_vm.prefix | default('') }}"
    suffix: "{{ cohesity_clone_vm.suffix | default('') }}"
  tags: always
  ```

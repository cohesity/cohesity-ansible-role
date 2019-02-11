# Task: Cohesity Protection Source Management

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Ansible Variables](#Ansible-Variables)
- [Customize Your Playbooks](#Customize-your-playbooks)
  - [Create new Physical Protection Sources using the Ansible Inventory](#Create-new-Physical-Protection-Sources-using-the-Ansible-Inventory)
  - [Create new VMware vCenter Protection Source](#Create-new-VMware-vCenter-Protection-Source)
  - [Create new NFS Protection Source](#Create-new-NFS-Protection-Source)
- [How the Task Works](#How-the-Task-works)

## Synopsis
[top](#task-cohesity-protection-source-management)

Use this task to add and configure Cohesity Protection Sources.

#### How It Works
- The task starts by determining if the named endpoint exists in the cluster.
- Upon validation, the task creates a new Protection Source (*state=present*) or removes the existing Protection Source (*state=absent*) from the cluster.
> **IMPORTANT**!<br>
  When *state=absent*, there are no job validations or state checks to ensure that backups are not running.  If jobs exist for the Source, an error is raised and the task fails.

### Requirements
[top](#task-cohesity-protection-source-management)

* Cohesity DataPlatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Before using this task, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

## Ansible Variables
[top](#task-cohesity-protection-source-management)

The following is a list of variables and the configuration expected when leveraging this task in your playbook.  For more information on these variables, see [Cohesity Protection Source](../modules/cohesity_source.md?id=syntax).
```yaml
cohesity_source:
  state: present
  endpoint: ""
  environment: ""
  host_type: ""
  vmware_type: ""
  source_username: ""
  source_password: ""
  nas_protocol: ""
  nas_username: ""
  nas_password: ""
```
## Customize Your Playbooks
[top](#task-cohesity-protection-source-management)

This example shows how to include the Cohesity Ansible role in your custom playbooks and leverage this task as part of the delivery.

### Create new Physical Protection Sources using the Ansible Inventory
[top](#task-cohesity-protection-source-management)

This is an example playbook that creates new Protection Sources for all Linux hosts based on the registered inventory hostname. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

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
    gather_facts: no
    roles:
        - cohesity_ansible_role
    tasks:
      - name: Configure Cohesity Protection Source on each Linux Physical Server
        include_role:
            name: cohesity_ansible_role
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_source:
                state: present
                endpoint: "{{ hostvars[item]['ansible_host'] }}"
                host_type: "Linux"
        with_items: "{{ groups.linux }}"
        tags: [ 'cohesity', 'sources', 'register', 'linux' ]
```

### Create new VMware vCenter Protection Source
[top](#task-cohesity-protection-source-management)

This is an example playbook that creates new Protection Sources for the chosen vCenter host. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

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
        var_vcenter_server: myvcenter.cohesity.lab
        var_vcenter_username: administrator
        var_vcenter_password: secret
    gather_facts: no
    roles:
        - cohesity_ansible_role
    tasks:
      - name: Configure Cohesity Protection Source on VMware vCenter Host
        include_role:
            name: cohesity_ansible_role
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_source:
                state: present
                endpoint: "{{var_vcenter_server }}"
                environment: "VMware"
                vmware_type: "VCenter"
                source_username: "{{ var_vcenter_username }}"
                source_password: "{{ var_vcenter_password }}"
        tags: [ 'cohesity', 'sources', 'register', 'vmware' ]
```

### Create new NFS Protection Source
[top](#task-cohesity-protection-source-management)

This is an example playbook that creates new Protection Sources for the chosen vCenter host. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

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
        var_export_path: 10.2.x.x:/export_path
        var_vcenter_username: administrator
        var_vcenter_password: secret
    gather_facts: no
    roles:
        - cohesity_ansible_role
    tasks:
      - name: Configure Cohesity Protection Source on NFS Export
        include_role:
            name: cohesity_ansible_role
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_source:
                state: present
                endpoint: "{{ var_export_path }}"
                environment: "GenericNAS"
                nas_protocol: "NFS"
        tags: [ 'cohesity', 'sources', 'register', 'nfs' ]
```


## How the Task Works
[top](#task-cohesity-protection-source-management)

The following information is copied directly from the included task in this role.  The source file is located at the root of this role in `/tasks/source.yml`.
```yaml
---
- name: "Cohesity Protection Source: Set {{ cohesity_source.endpoint | default('endpoint') }} to state of {{ cohesity_source.state | default('present') }}"
  cohesity_source:
    cluster: "{{ cohesity_server }}"
    username: "{{ cohesity_admin }}"
    password: "{{ cohesity_password }}"
    validate_certs: "{{ cohesity_validate_certs }}"
    state:  "{{ cohesity_source.state | default('present') }}"
    endpoint: "{{ cohesity_source.endpoint | default('') }}"
    environment: "{{ cohesity_source.environment | default('Physical') }}"
    host_type: "{{ cohesity_source.host_type | default('Linux') }}"
    vmware_type: "{{ cohesity_source.vmware_type | default('VCenter') }}"
    source_username: "{{ cohesity_source.source_username | default('') }}"
    source_password: "{{ cohesity_source.source_password | default('') }}"
    nas_protocol: "{{ cohesity_source.nas_protocol | default('NFS') }}"
    nas_username: "{{ cohesity_source.nas_username | default('') }}"
    nas_password: "{{ cohesity_source.nas_password | default('') }}"
  tags: always

```

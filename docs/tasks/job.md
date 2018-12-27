# Task: Cohesity Protection Job Management

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Ansible Variables](#Ansible-Variables)
- [Customizing your playbooks](#Customizing-your-playbooks)
  - [Creation of new Physical Protection Job using the Ansible Inventory](#Creation-of-new-Physical-Protection-Job-using-the-Ansible-Inventory)
  - [Creation of new VMware vCenter Protection Job](#Creation-of-new-VMware-vCenter-Protection-Job)
  - [Start an On-Demand Protection Job for VMware Source](#Start-an-On-Demand-Protection-Job-for-VMware-Source)
  - [Delete an existing Protection Job for Physical Source](#Delete-an-existing-Protection-Job-for-Physical-Source)
- [How the Task works](#How-the-Task-works)

## SYNOPSIS
[top](#task-cohesity-protection-job-management)

This task can be used to add and configure Cohesity Protection Sources

#### How it works
- The task starts by determining if the named endpoint exists in the cluster
- Upon validation, the task will create a new Protection Source (*state=present*) or remove the existing Protection Source (*state=absent*) from the Cluster.
> **IMPORTANT**!<br>
  When *state=absent*, there are no job validations nor state checks to ensure that backups are not running.  If jobs exist for the Source, an error will be raised and the task will fail.

### Requirements
[top](#task-cohesity-protection-job-management)

* Cohesity Cluster running version 6.0 or higher
* Ansible >= 2.6
  * [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a unix system running any of the following operating systems: Linux (Red Hat, Debian, CentOS), macOS, any of the BSDs. Windows isn’t supported for the control machine.
* Python >= 2.6

> **Notes**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Prior to using theis task, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.

## Ansible Variables
[top](#task-cohesity-protection-job-management)

The following is a list of variables and the configuration expected when leveraging this task in your playbook.  For more information on these variables, see the [official Cohesity Ansible module documentation](/modules/cohesity_job.md?id=syntax)
```yaml
cohesity_protection:
  state: present
  job_name: ""
  endpoint: ""
  environment: ""
  storage_domain: DefaultIddStorageDomain
  policy: Bronze
  delete_backups: False
  cancel_active: False
```
## Customizing your playbooks
[top](#task-cohesity-protection-job-management)

This example show how to include the Cohesity-Ansible role in your custom playbooks and leverage this task as part of the delivery.

### Creation of new Physical Protection Job using the Ansible Inventory
[top](#task-cohesity-protection-job-management)

Here is an example playbook that creates new Protection Job for all Physical hosts based on the registered inventory hostname. Please change it as per your environment.
> **Note:**
  - Prior to using these example playbooks, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.
  - This example requires that the endpoint matches an existing Protection Source.  See [more information on sources here](/tasks/source.md)

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
        - cohesity.ansible
    tasks:
      - name: Create new Protection Jobs for each Physical Server
        include_role:
          name: cohesity.ansible
          tasks_from: job
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_protection:
                state: present
                job_name: "{{ hostvars[item]['ansible_host'] }}"
                endpoint: "{{ hostvars[item]['ansible_host'] }}"
        with_items: "{{ groups.physical }}"
        tags: [ 'cohesity', 'jobs', 'register', 'physical' ]
```

### Creation of new VMware vCenter Protection Job
[top](#task-cohesity-protection-job-management)

Here is an example playbook that creates new Protection Jopb for the chosen vCenter host. Please change it as per your environment.
> **Note:**
  - Prior to using these example playbooks, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.

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
        var_job_name: myvcenter.cohesity.lab
        var_endpoint: myvcenter.cohesity.lab
    gather_facts: no
    roles:
        - cohesity.ansible
    tasks:
      - name: Create new Protection Jobs for chosen VMware Server
        include_role:
          name: cohesity.ansible
          tasks_from: job
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_protection:
                state: present
                job_name: "{{ var_job_name }}"
                endpoint: "{{ var_endpoint }}"
                environment: "VMware"
        tags: [ 'cohesity', 'jobs', 'register', 'vmware' ]
```

### Start an On-Demand Protection Job for VMware Source
[top](#task-cohesity-protection-job-management)

Here is an example playbook that creates new Protection Sources for the chosen vCenter host. Please change it as per your environment.
> **Note:**
  - Prior to using these example playbooks, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.

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
        var_job_name: myvcenter.cohesity.lab
    gather_facts: no
    roles:
        - cohesity.ansible
    tasks:
      - name: Configure Cohesity Protection Source on NFS Export
        include_role:
            name: cohesity.ansible
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_source:
                state: started
                job_name: "{{ var_job_name }}"
                environment: "VMware"
        tags: [ 'cohesity', 'jobs', 'start', 'vmware' ]
```

### Delete an existing Protection Job for Physical Source
[top](#task-cohesity-protection-job-management)

Here is an example playbook that creates new Protection Sources for the chosen vCenter host. Please change it as per your environment.
> **Note:**
  - Prior to using these example playbooks, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.

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
        var_job_name: windows01.cohesity.lab
        var_delete_backups: True
    gather_facts: no
    roles:
        - cohesity.ansible
    tasks:
      - name: Configure Cohesity Protection Source on NFS Export
        include_role:
            name: cohesity.ansible
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_source:
                state: absent
                job_name: "{{ var_job_name }}"
                environment: "Physical"
                delete_backups: "{{ var_delete_backups }}"
        tags: [ 'cohesity', 'jobs', 'remove', 'physical' ]
```


## How the Task works
[top](#task-cohesity-protection-job-management)

The following information is copied directly from the included task in this role.  The source file can be found at the root of this repo in `/tasks/job.yml`
```yaml
---
- name: "Cohesity Protection Job: Set {{ cohesity_protection.job_name | default('job_name') }} to state of {{ cohesity_protection.state | default('present') }}"
  cohesity_job:
    cluster: "{{ cohesity_server }}"
    username: "{{ cohesity_admin }}"
    password: "{{ cohesity_password }}"
    validate_certs: "{{ cohesity_validate_certs }}"
    state:  "{{ cohesity_protection.state | default('present') }}"
    name: "{{ cohesity_protection.job_name | default('') }}"
    environment: "{{ cohesity_protection.environment | default('Physical') }}"
    protection_sources:
      - "{{ cohesity_protection.endpoint | default('') }}"
    protection_policy: "{{ cohesity_protection.policy | default('Bronze') }}"
    storage_domain: "{{ cohesity_protection.storage_domain | default('DefaultIddStorageDomain') }}"
    delete_backups: "{{ cohesity_protection.delete_backups | default(False) }}"
    cancel_active: "{{ cohesity_protection.cancel_active | default(False) }}"
  tags: always

```
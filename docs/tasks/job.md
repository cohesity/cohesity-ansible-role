# Task: Cohesity Protection Job Management

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Ansible Variables](#Ansible-Variables)
- [Customize Your Playbooks](#Customize-your-playbooks)
  - [Create new Physical Protection Job using the Ansible Inventory](#Create-new-Physical-Protection-Job-using-the-Ansible-Inventory)
  - [Create new VMware vCenter Protection Job](#Create-new-VMware-vCenter-Protection-Job)
  - [Start an On-Demand Protection Job for VMware Source](#Start-an-On-Demand-Protection-Job-for-VMware-Source)
  - [Delete an existing Protection Job for Physical Source](#Delete-an-existing-Protection-Job-for-Physical-Source)
- [How the Task Works](#How-the-Task-works)

## Synopsis
[top](#task-cohesity-protection-job-management)

Use this task to add and configure Cohesity Protection Jobs.

#### How It Works
- The task starts by determining whether named protection job exists in the cluster.
- Upon validation, the task creates a new Protection job or add physical sources to existing job (*state=present*) or removes the existing Protection job (*state=absent*) from the cluster.
> **IMPORTANT**!<br>
  When *state=absent*, there are no job validations or state checks to ensure that backups are not running. If job exist and an physical source endpoint is given, the task tries to remove source from the job 

### Requirements
[top](#task-cohesity-protection-job-management)

* Cohesity Cluster running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Before using this task, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

## Ansible Variables
[top](#task-cohesity-protection-job-management)

The following is a list of variables and the configuration expected when leveraging this task in your playbook.  For more information on these variables, see [Cohesity Protection Job](/modules/cohesity_job.md?id=syntax).
```yaml
cohesity_protection:
  state: present
  job_name: ""
  sources:
     - endpoint: ""
  environment: ""
  storage_domain: DefaultIddStorageDomain
  policy: Bronze
  delete_backups: False
  cancel_active: False
```
## Customize Your Playbooks
[top](#task-cohesity-protection-job-management)

This example shows how to include the Cohesity Ansible Role in your custom playbooks and leverage this task as part of the delivery.

### Create new Physical Protection Job using the Ansible Inventory
[top](#task-cohesity-protection-job-management)

This is an example playbook that creates a new Protection Job and adds Physical hosts to the job based on the registered inventory hostname. (Remember to change it to suit your environment.)
> **Notes:**
  - Before using these example playbooks, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.
  - This example requires that the endpoints matches existing Protection Sources.  See [Task: Cohesity Protection Source Management](tasks/source.md).
  - Make sure includeFilePath and excludeFilePaths exist on the sources

Following inventory file can be used in the ansible-playbook runs below. Copy the content to `inventory.ini` file
```ini
[workstation]
127.0.0.1 ansible_connection=local

[linux]
10.21.143.240
10.21.143.241

[linux:vars]
ansible_user=cohesity
```
You can create a file called `protection_job_physical.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> protection_job_physical.yml -e "username=abc password=abc"
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
    gather_facts: no
    roles:
        - cohesity.cohesity_ansible_role
    tasks:
      - name: Create new Protection Job for Physical Linux Servers
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_protection:
                state: present
                job_name: "protect_physical_linux"
                sources:
                    - endpoint: "{{ item }}"
                      paths:
                        - includeFilePath: "/home"
                          excludeFilePaths:
                            - "/home/cohesity/cohesityagent"
                            - "/home/Documents"
                          skipNestedVolumes: False
                environment: "PhysicalFiles"   
        with_items: "{{ groups['linux'] }}"
        tags: [ 'cohesity', 'jobs', 'register', 'physical' ]
```

### Create new VMware vCenter Protection Job
[top](#task-cohesity-protection-job-management)

This is an example playbook that creates a new Protection Job for the chosen vCenter host. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

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
        var_vcenter_server: myvcenter.cohesity.lab
        var_vcenter_username: administrator
        var_vcenter_password: secret
        var_job_name: myvcenter.cohesity.lab
        var_endpoint: myvcenter.cohesity.lab
    gather_facts: no
    roles:
        - cohesity.cohesity_ansible_role
    tasks:
      - name: Create new Protection Job for chosen VMware Server
        include_role:
          name: cohesity.cohesity_ansible_role
          tasks_from: job
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_protection:
                state: present
                job_name: "{{ var_job_name }}"
                sources: 
                  - endpoint: "{{ var_endpoint }}"
                environment: "VMware"
        tags: [ 'cohesity', 'jobs', 'register', 'vmware' ]
```

### Start an On-Demand Protection Job for VMware Source
[top](#task-cohesity-protection-job-management)

This is an example playbook that starts an existing VMware protection job. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

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
        var_job_name: myvcenter.cohesity.lab
    gather_facts: no
    roles:
        - cohesity.cohesity_ansible_role
    tasks:
      - name: Start protection job
        include_role:
            name: cohesity.cohesity_ansible_role
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

This is an example playbook that deletes a Protection job. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

```yaml
---
  - hosts: workstation
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: {{ username }}
        var_cohesity_password: {{ password }}
        var_validate_certs: False
        var_job_name: protect_physical_linux
        var_delete_backups: True
    gather_facts: no
    roles:
        - cohesity.cohesity_ansible_role
    tasks:
      - name: Delete protection job
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: source
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_source:
                state: absent
                job_name: "{{ var_job_name }}"
                environment: "PhysicalFiles"
                delete_backups: "{{ var_delete_backups }}"

```


## How the Task Works
[top](#task-cohesity-protection-job-management)

The following information is copied directly from the included task in this role.  The source file is located at the root of this role in `/tasks/job.yml`.
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
    environment: "{{ cohesity_protection.environment | default('PhysicalFiles') }}"
    protection_sources: "{{ cohesity_protection.sources | default('') }}"
    protection_policy: "{{ cohesity_protection.policy | default('Bronze') }}"
    storage_domain: "{{ cohesity_protection.storage_domain | default('DefaultIddStorageDomain') }}"
    delete_backups: "{{ cohesity_protection.delete_backups | default(False) }}"
    cancel_active: "{{ cohesity_protection.cancel_active | default(False) }}"
    exclude: "{{cohesity_protection.exclude | default('') }}"
    include: "{{cohesity_protection.include | default('') }}"
  tags: always

```

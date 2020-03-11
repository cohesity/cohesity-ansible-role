# Task: Cohesity Policy Management 

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Ansible Variables](#Ansible-Variables)
- [Customize Your Playbooks](#Customize-your-playbooks)
 - Policy Management
    - [Create a Protection Policy](#Create-a-Protection-Policy)
    - [Modify a Protection Policy](#Modify-a-Protection-Policy)
    - [Delete a Protection Policy](#Delete-a-Protection-Policy)
- [How the Task Works](#How-the-Task-works)

## Synopsis
[top](#Cohesity-policy-management)

Use this task to clone a VM using Test/Dev workflow

#### How It Works
- The tasks collects all the information (required and optional) and starts a clone task (if *state=present*).
- The task can also destory a clone (*state=absent*) that was cloned using Test/Dev workflow.


### Requirements
[top](#Cohesity-policy-management)

* Cohesity DataPlatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Before using this task, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

## Ansible Variables
[top](#Cohesity-policy-management)

The following is a list of variables and the configuration expected when using this task in your playbook.  For more information on these variables, see [Cohesity Policy Management](../modules/cohesity_clone.md?id=syntax).
```yaml
- cohesity_policy:
    name: POLICY_NAME
    incremental_backup_schedule: ASK_TEAM
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
```

## Customize Your Playbooks
[top](#Cohesity-policy-management)

These examples show how to include the Cohesity Ansible Role in your custom playbooks and leverage this task as part of the delivery.

Following inventory file can be used for the ansible-playbook runs below. Copy the content to `inventory.ini` file
```ini
[workstation]
127.0.0.1 ansible_connection=local

[cohesity]
10.21.143.240
```

### Create a Protection Policy
[top](#Cohesity-policy-management)

This is an example playbook that creates a Protection Policy on the `Cohesity` hosts. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

You can create a file called `cohesity-policy.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> cohesity-policy.yml -e "username=abc password=abc"
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
      - name: Create a Clone VM task using Test/Dev Workflow
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: policy
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_policy:
                name: POLICY_NAME
                incremental_backup_schedule: ASK_TEAM
                cluster: cohesity.lab
                username: admin
                password: password
                state: present
```

### Modify a Protection Policy
[top](#Cohesity-policy-management)

This is an example playbook that modify a Protection Policy on the `Cohesity` hosts. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

You can create a file called `cohesity-policy.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> cohesity-policy.yml -e "username=abc password=abc"
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
      - name: Create a Clone VM task using Test/Dev Workflow
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: policy
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_policy:
                name: POLICY_NAME
                incremental_backup_schedule: ASK_TEAM
                cluster: cohesity.lab
                username: admin
                password: password
                state: present
```

### Delete a Protection Policy
[top](#Cohesity-policy-management)

This is an example playbook that deletes the Protection Policy on all `cohesity` hosts. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

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
      - name: Create a Clone VM task using Test/Dev Workflow
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: policy
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_policy:
                name: POLICY_NAME
                incremental_backup_schedule: ASK_TEAM
                cluster: cohesity.lab
                username: admin
                password: password
                state: absent
```

## How the Task Works
[top](#Cohesity-policy-management)

The following information is copied directly from the included task in this role.  The source file is located at the root of this role in `/tasks/policy.yml`.
```yaml
---
- name: "Cohesity Protection Policy: Set {{ cohesity_policy.name | default('policy_name') }} to state of {{ cohesity_policy.state | default('present') }}"
  cohesity_policy:
    cluster: "{{ cohesity_server }}"
    username: "{{ cohesity_admin }}"
    password: "{{ cohesity_password }}"
    state: "{{ cohesity_policy.state | default('present') }}"
    name: "{{ cohesity_policy.name | default('') }}"
    description: "{{ cohesity_policy.description | default('') }}"
    days_to_retain: "{{ cohesity_policy.days_to_retain | default(90) }}"
    retries: "{{ cohesity_policy.retries | default(3) }}"
    retry_interval: "{{ cohesity_policy.retry_interval | default(30) }}"
    incremental_backup_schedule: "{{ cohesity_policy.incremental_backup_schedule }}"
    full_backup_schedule: "{{ cohesity_policy.full_backup_schedule | default('') }}"
    blackout_window: "{{ cohesity_policy.blackout_window | default('') }}"
    bmr_backup_schedule: "{{ cohesity_policy.bmr_backup_schedule | default('') }}"
    log_backup_schedule: "{{ cohesity_policy.log_backup_schedule | default('') }}"
    extended_retention: "{{ cohesity_policy.extended_retention | default('') }}"
    archival_copy: "{{ cohesity_policy.archival_copy | default('') }}"
  tags: always
  ```

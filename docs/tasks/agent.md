# Task: Cohesity Agent Management - Linux

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Ansible Variables](#Ansible-Variables)
- [Customize Your Playbooks](#Customize-your-playbooks)
  - [Install the Cohesity Agent on Linux hosts](#Install-the-Cohesity-Agent-on-Linux-hosts)
  - [Install the Cohesity Agent on Linux hosts using Root](#Install-the-Cohesity-Agent-on-Linux-hosts-using-Root)
  - [Install the Cohesity Agent on Linux hosts using a custom download path](#Install-the-Cohesity-Agent-on-Linux-hosts-using-a-custom-download-path)
- [How the Task Works](#How-the-Task-works)

## Synopsis
[top](#task-cohesity-agent-management---linux)

Use this task to install the required packages on Ubuntu/Debian and CentOS/RHEL servers and manage the Cohesity Agent.

#### How It Works
- The task starts by installing the required packages on the Ubuntu/Debian or CentOS/RHEL server and enabling tcp port 50051 in firewall (if *state=present*).
- Upon completion, the latest version of the agent is installed (*state=present*) or removed (*state=absent*) from the `linux` server.

### Requirements
[top](#task-cohesity-agent-management---linux)

* Cohesity DataPlatform running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Before using this task, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

## Ansible Variables
[top](#task-cohesity-agent-management---linux)

The following is a list of variables and the configuration expected when using this task in your playbook.  For more information on these variables, see [Cohesity Agent Management - Linux](../modules/cohesity_agent.md?id=syntax).
```yaml
cohesity_agent:
  state: "present"
  service_user: "cohesityagent"
  service_password: ""
  service_group: "cohesityagent"
  create_user: True
  download_location: ""
```
## Customize Your Playbooks
[top](#task-cohesity-agent-management---linux)

These examples show how to include the Cohesity Ansible Role in your custom playbooks and leverage this task as part of the delivery.

### Install the Cohesity Agent on Linux hosts
[top](#task-cohesity-agent-management---linux)

This is an example playbook that installs the Cohesity agent on all `linux` hosts. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../setup.md) and [How to Use](../how-to-use.md) sections of this guide.

You can create a file called `cohesity-agent-linux.yml`, add the contents from the sample playbook, and then run the playbook using `ansible-playbook`:
  ```
  ansible-playbook -i <inventory_file> cohesity-agent-linux.yml -e "username=admin password=admin"
  ```

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
      - name: Install new Cohesity Agent on each Linux Physical Server
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: agent
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_agent:
                state: present
```

### Install the Cohesity Agent on Linux hosts using Root
[top](#task-cohesity-agent-management---linux)

This is an example playbook that installs the Cohesity agent on all `linux` hosts using the Root account. (Remember to change it to suit your environment.)
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
      - name: Install new Cohesity Agent on each Linux Physical Server
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: agent
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_agent:
                state: present
                service_user: "root"
                service_group: "root"
                create_user: False
```


### Install the Cohesity Agent on Linux hosts using a custom download path
[top](#task-cohesity-agent-management---linux)

This is an example playbook that installs the Cohesity agent on all `linux` hosts using a custom download location. (Remember to change it to suit your environment.)
> **Notes:**
  - When using the default download location, the Cohesity agent installer is placed in `/tmp/<temp-dir`.  If your environment prevents the use of `/tmp` with a `noexec` option, then you must select an alternate location.
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
      - name: Install new Cohesity Agent on each Linux Physical Server
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: agent
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_agent:
                state: present
                download_location: "/opt/cohesity/download/"
        tags: [ 'cohesity', 'agent', 'install', 'physical', 'linux' ]
```

## How the Task Works
[top](#task-cohesity-agent-management---linux)

The following information is copied directly from the included task in this role.  The source file is located at the root of this role in `/tasks/agent.yml`.
```yaml
---
- name: Install Prerequisite Packages for CentOS
  yum:
    name: "wget,rsync,lsof,lvm2,nfs-utils"
    state: present
  when:
    - ansible_distribution == "CentOS"
    - cohesity_agent.state == "present"
  tags: always

- name: Install Prerequisite Packages for Ubuntu
  yum:
    name: "wget,rsync,lsof,lvm2,nfs-common"
    state: present
  when:
    - ansible_distribution == "Ubuntu"
    - cohesity_agent.state == "present"
  tags: always

- name: Enable tcp port 50051 for CentOS
  command: "firewall-cmd {{ item }}"
  with_items:
  - --zone=public --permanent --add-port 50051/tcp
  - --reload
  when:
      - ansible_distribution == "CentOS"
      - cohesity_agent.state == "present"
  tags: always

- name: Enable tcp port 50051 for Ubuntu
  command: ufw allow 50051/tcp
  when:
      - ansible_distribution == "Ubuntu"
      - cohesity_agent.state == "present"
  tags: always

- name: "Cohesity agent: Set Agent to state of {{ cohesity_agent.state | default('present') }}"
  cohesity_agent:
    cluster: "{{ cohesity_server }}"
    username: "{{ cohesity_admin }}"
    password: "{{ cohesity_password }}"
    validate_certs: "{{ cohesity_validate_certs | default(False) }}"
    state: "{{ cohesity_agent.state }}"
    service_user: "{{ cohesity_agent.service_user | default('cohesityagent') }}"
    service_group: "{{ cohesity_agent.service_group | default('cohesityagent') }}"
    create_user: "{{ cohesity_agent.create_user | default(True) }}"
    download_location: "{{ cohesity_agent.download_location | default() }}"
  tags: always
```

# Task: Cohesity Agent Management - Linux

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Ansible Variables](#Ansible-Variables)
- [Customizing your playbooks](#Customizing-your-playbooks)
  - [Installation of Cohesity Agent on Linux hosts](#Installation-of-Cohesity-Agent-on-Linux-hosts)
  - [Installation of Cohesity Agent on Linux hosts installed using Root](#Installation-of-Cohesity-Agent-on-Linux-hosts-installed-using-Root)
  - [Installation of Cohesity Agent on Linux hosts installed using Root using a custom download path](#Installation-of-Cohesity-Agent-on-Linux-hosts-using-a-custom-download-path)
- [How the Task works](#How-the-Task-works)

## SYNOPSIS
[top](#task-cohesity-agent-management-linux)

This task can be used to install the required pre-requisite packages on Ubuntu/Debian and CentOS/RHEL servers and manage the Cohesity Agent

#### How it works
- The task starts by install the required pre-requisite packages on the Ubuntu/Debian or CentOS/RHEL server (if *state=present*).
- Upon completion, the latest version of the agent will be installed (*state=present*) or removed (*state=absent*) from the `linux` server.

### Requirements
[top](#task-cohesity-agent-management-linux)

* Cohesity Cluster running version 6.0 or higher
* Ansible >= 2.6
  * [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a unix system running any of the following operating systems: Linux (Red Hat, Debian, CentOS), macOS, any of the BSDs. Windows isn’t supported for the control machine.
* Python >= 2.6

> **Notes**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Prior to using theis task, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.

## Ansible Variables
[top](#task-cohesity-agent-management-linux)

The following is a list of variables and the configuration expected when leveraging this task in your playbook.  For more information on these variables, see the [official Cohesity Ansible module documentation](/modules/cohesity_agent.md?id=syntax)
```yaml
cohesity_agent:
  state: "present"
  service_user: "cohesityagent"
  service_password: ""
  service_group: "cohesityagent"
  create_user: True
  download_location: ""
```
## Customizing your playbooks
[top](#task-cohesity-agent-management-linux)

This example show how to include the Cohesity-Ansible role in your custom playbooks and leverage this task as part of the delivery.

### Installation of Cohesity Agent on Linux hosts
[top](#task-cohesity-agent-management-linux)

Here is an example playbook that installs the Cohesity agent on all `linux` hosts. Please change it as per your environment.
> **Note:**
  - Prior to using these example playbooks, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.

```yaml
---
  - hosts: linux
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: admin
        var_cohesity_password: admin
        var_validate_certs: False
    become: true
    roles:
        - cohesity.ansible
    tasks:
      - name: Install new Cohesity Agent on each Linux Physical Server
        include_role:
            name: cohesity.ansible
            tasks_from: agent
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_agent:
                state: present
        tags: [ 'cohesity', 'agent', 'install', 'physical', 'linux' ]
```

### Installation of Cohesity Agent on Linux hosts installed using Root
[top](#task-cohesity-agent-management-linux)

Here is an example playbook that installs the Cohesity agent on all `linux` hosts using the Root account. Please change it as per your environment.
> **Note:**
  - Prior to using these example playbooks, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.

```yaml
---
  - hosts: linux
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: admin
        var_cohesity_password: admin
        var_validate_certs: False
    become: true
    roles:
        - cohesity.ansible
    tasks:
      - name: Install new Cohesity Agent on each Linux Physical Server
        include_role:
            name: cohesity.ansible
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
        tags: [ 'cohesity', 'agent', 'install', 'physical', 'linux' ]
```


### Installation of Cohesity Agent on Linux hosts using a custom download path
[top](#task-cohesity-agent-management-linux)

Here is an example playbook that installs the Cohesity agent on all `linux` hosts using a custom download location. Please change it as per your environment.
> **Note:**
  - When using the default download location, the Cohesity agent installer will be place in `/tmp/<temp-dir` location.  If your environment prevents the use of `/tmp` with a `noexec` option, then the alternate location must be set.
  - Prior to using these example playbooks, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.

```yaml
---
  - hosts: linux
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: admin
        var_cohesity_password: admin
        var_validate_certs: False
    become: true
    roles:
        - cohesity.ansible
    tasks:
      - name: Install new Cohesity Agent on each Linux Physical Server
        include_role:
            name: cohesity.ansible
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

## How the Task works
[top](#task-cohesity-agent-management-linux)

The following information is copied directly from the included task in this role.  The source file can be found at the root of this repo in `/tasks/agent.yml`
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

- name: "Cohesity agent: Set Agent to state of {{ cohesity_agent.state | default('present') }}"
  cohesity_agent:
    cluster: "{{ cohesity_server }}"
    username: "{{ cohesity_admin }}"
    password: "{{ cohesity_password }}"
    validate_certs: "{{ cohesity_validate_certs }}"
    state: "{{ cohesity_agent.state }}"
    service_user: "{{ cohesity_agent.service_user | default('cohesityagent') }}"
    service_group: "{{ cohesity_agent.service_group | default('cohesityagent') }}"
    create_user: "{{ cohesity_agent.create_user | default(True)}}"
    download_location: "{{ cohesity_agent.download_location | default() }}"
  tags: always
```
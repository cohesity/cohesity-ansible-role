# Task: Cohesity Agent Management - Windows

[Go back to Documentation home page ](../README.md)

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Ansible Variables](#Ansible-Variables)
- [Customize Your Playbooks](#Customize-your-playbooks)
  - [Install the Cohesity Agent on Windows hosts](#Install-the-Cohesity-Agent-on-Windows-hosts)
  - [Install the Cohesity Agent on Windows hosts using a service account](#Install-the-Cohesity-Agent-on-Windows-hosts-using-a-service-account)
- [How the Task Works](#How-the-Task-works)

## Synopsis
[top](#task-cohesity-agent-management---windows)

Use this task to install and manage the Cohesity Agent on Windows hosts.

#### How It Works
- The task starts by installing the latest version of the agent (when *state=present*) or removing it from the `windows` server (when *state=absent*).
- If *state=present*, then the Windows Firewall rule will be updated to allow the Cohesity Agent to communicate with the Cohesity cluster.
- When the *installer_type=volcbt* and *cohesity_agent.reboot=True*, the host is rebooted to allow the driver to load (*state=present*) or unload (*state=absent*).

### Requirements
[top](#task-cohesity-agent-management---windows)

* Cohesity Cluster running version 6.0 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Powershell version 4.0 or higher
* Agent installation is supported only on the operating systems listed on https://docs.cohesity.com where select your `DataPlatform` version -> `Release Notes` -> `Supported Software` -> `Physical Servers` section

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Prior to using theis task, refer to the [Setup](../common/setup.md) and [How to Use](../common/how-to-use.md) sections of this guide.

## Ansible Variables
[top](#task-cohesity-agent-management---windows)

The following is a list of variables and the configuration expected when leveraging this task in your playbook.  For more information on these variables, see [Cohesity Agent Management - Windows](../library/cohesity_win_agent.md).
```yaml
cohesity_agent:
  state: "present"
  service_user: "cohesityagent"
  service_password: ""
  install_type: "volcbt"
  preservesettings: False
  reboot: True
```
## Customize Your Playbooks
[top](#task-cohesity-agent-management---windows)

This example shows how to include the Cohesity Ansible role in your custom playbooks and leverage this task as part of the delivery.

### Install the Cohesity Agent on Windows hosts
[top](#task-cohesity-agent-management---windows)

This is an example playbook that installs the Cohesity agent on all `windows` hosts. (Remember to change it to suit your environment.)
> **Note:**
  - Prior to using these example playbooks, refer to the [Setup](../common/setup.md) and [How to Use](../common/how-to-use.md) sections of this guide.

```yaml
---
  - hosts: windows
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: admin
        var_cohesity_password: admin
        var_validate_certs: False
    gather_facts: no
    roles:
        - cohesity.cohesity_ansible_role
    tasks:
      - name: Install new Cohesity Agent on each Windows Physical Server
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: win_agent
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_agent:
                state: present
                reboot: True
        tags: [ 'cohesity', 'agent', 'install', 'physical', 'windows' ]
```

### Install the Cohesity Agent on Windows hosts using a service account
[top](#task-cohesity-agent-management---windows)

This is an example playbook that installs the Cohesity Agent on all `windows` hosts using a service account and the `filecbt` driver. (Remember to change it to suit your environment.)
> **Note:**
  - Before using these example playbooks, refer to the [Setup](../common/setup.md) and [How to Use](../common/how-to-use.md) sections of this guide.

```yaml
---
  - hosts: windows
    # => Please change these variables to connect
    # => to your Cohesity Cluster
    vars:
        var_cohesity_server: cohesity_cluster_vip
        var_cohesity_admin: admin
        var_cohesity_password: admin
        var_validate_certs: False
        var_service_user: "cohesity\\svc_account"
        var_service_password: "secret"
    gather_facts: no
    roles:
        - cohesity.cohesity_ansible_role
    tasks:
      - name: Install new Cohesity Agent on each Windows Physical Server
        include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: win_agent
        vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_agent:
                state: present
                service_user: "{{ var_service_user }}"
                service_password: "{{ var_service_password }}"
                install_type: "filecbt"
                reboot: False
        tags: [ 'cohesity', 'agent', 'install', 'physical', 'windows' ]
```

## How the Task Works
[top](#task-cohesity-agent-management---windows)

The following information is copied directly from the included task in this role.  The source file is located at the root of this role in `/tasks/win_agent.yml`
```yaml
---
- name: "Cohesity agent: Set Agent to state of {{ cohesity_agent.state | default('present') }}"
  cohesity_win_agent:
    cluster: "{{ cohesity_server }}"
    username: "{{ cohesity_admin }}"
    password: "{{ cohesity_password }}"
    validate_certs: "{{ cohesity_validate_certs }}"
    state: "{{ cohesity_agent.state }}"
    service_user: "{{ cohesity_agent.service_user | default('') }}"
    service_password: "{{ cohesity_agent.service_password | default('') }}"
    preservesettings: "{{ cohesity_agent.preservesettings | default(False)}}"
    install_type: "{{ cohesity_agent.install_type | default('volcbt') }}"
  tags: always
  register: installed

- name: Firewall rule to allow CohesityAgent on TCP port 50051
  win_firewall_rule:
    name: Cohesity Agent Ansible
    description:
      - Automated Firewall rule created by the Cohesity Ansible integration to allow
      - for the Cohesity Agent to communicate through the firewall.
    localport: 50051
    action: allow
    direction: in
    protocol: tcp
    state: "{{ cohesity_agent.state }}"
    enabled: yes
  tags: always

# => This reboot will only be triggered if both of the following conditions are true:
# => - The registered variable 'installed' returns True when the changed state is queried.
# => - The user defined variable 'cohesity_win_agent_reboot' returns as True.
- name: Reboot the Hosts after agent modification
  win_reboot:
    reboot_timeout: 180
  when:
    - installed.changed
    - cohesity_agent.reboot
  tags: always
```

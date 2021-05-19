# Cohesity Oracle Protection Source

[Go back to Documentation home page ](../README.md)

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Syntax](#syntax)
- [Examples](#examples)
  - [Register a Oracle Cohesity Protection Source on a selected endpoint](#Register-a-Oracle-Cohesity-Protection-Source-on-a-selected-endpoint)
  - [Unregister an existing Oracle Protection Source](#Unregister-an-existing-Oracle-Protection-Source)
- [Parameters](#parameters)
- [Outputs](#outputs)
  - [Example return from a succesful registration of a Oracle Source](#Example-return-from-a-succesful-registration-of-a-Oracle-Source)
  - [Example return from the succesful unregistration of a Oracle Source](#Example-return-from-the-succesful-unregistration-of-a-Oracle-Source)

## Synopsis
[top](#cohesity-oracle-protection-source)

The Ansible Module registers or removes Cohesity Protection Sources to/from a Cohesity Cluster.  When executed in a playbook, the Cohesity Protection Source will be validated and the appropriate state action will be applied.

### Requirements
[top](#cohesity-oracle-protection-source)

* Cohesity DataPlatform version 6.4.1 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Note:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.

## Syntax
[top](#cohesity-oracle-protection-source)

```yaml
- cohesity_oracle_source:
    cluster: <ip or hostname for cohesity cluster>
    username: <username with cluster level permissions>
    password: <password for the selected user>
    validate_certs: <boolean to determine if SSL certificates should be validated>
    state: <state of the Protection Source>
    force_register: <boolean to determine if the source should be force_registered even if connection failed>
    endpoint: <ip or hostname or nas_path to be configured as a Protection Source>
    db_username: <username for the Oracle database>
    db_password: <password for the Oracle database>
```

## Examples
[top](#cohesity-oracle-protection-source)

### Register a Oracle Cohesity Protection Source on a selected endpoint
[top](#cohesity-oracle-protection-source)

```yaml
- cohesity_oracle_source:
    cluster: cohesity.lab
    username: admin
    password: password
    endpoint: mylinux.host.lab
    state: present
    force_register: True
    endpoint: orcl-serv2-eng-db.com
    db_username: oracle
    db_password: oracle

```

### Unregister an existing Oracle Protection Source
[top](#cohesity-oracle-protection-source)

```yaml
- cohesity_oracle_source:
    cluster: cohesity.lab
    username: admin
    password: password
    endpoint: orcl-serv2-eng-db.com
    state: absent

```


## Parameters
[top](#cohesity-oracle-protection-source)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity cluster |
| X | **username** | String | | Username with which Ansible will connect to the Cohesity cluster (username used to login to cluster from UI). Domain-specific credentials can be configured as.<br>- username@domain or domain/username (will be deprecated in future). |
| X | **password** | String | | Password belonging to the selected Username (password used to login to cluster from UI).  This parameter is not logged. |
|   | validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |
|   | state | Choice | -**present**<br>-absent | Determines the state of the Protection Source. |
| X | **endpoint** | String | | Specifies the network endpoint where the Protection Source is reachable. It can be the URL, fully qualified domain name or IP address. |
|   | force_register | Boolean | False | When *True*, forces the registration of the Cohesity Protection Source. |
|   | db_username | String | | Specifies the username of oracle database to login. **Required** when *state=present* |
|   | db_password | String | | Specifies the password of oracle database to login. **Required** when *state=present* |

## Outputs
[top](#cohesity-oracle-protection-source)

### Example return from a succesful registration of a Oracle Source
[top](#cohesity-oracle-protection-source)

```json
{
  "changed": true, 
  "invocation": {
      "module_args": {
          "cluster": "10.14.31.6", 
          "db_password": "", 
          "db_username": "", 
          "endpoint": "10.14.31.80", 
          "force_register": true, 
          "password": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER", 
          "state": "present", 
          "username": "admin", 
          "validate_certs": false
      }
  }, 
  "msg": "Registration of Cohesity Protection Source Complete"
}
```


### Example return from the succesful unregistration of a Oracle Source
[top](#cohesity-oracle-protection-source)

```json
{
    "changed": true, 
    "endpoint": "10.14.31.80", 
    "id": 1739, 
    "invocation": {
        "module_args": {
            "cluster": "10.14.31.6", 
            "db_password": "", 
            "db_username": "", 
            "endpoint": "10.14.31.80", 
            "force_register": false, 
            "password": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER", 
            "state": "absent", 
            "username": "admin", 
            "validate_certs": false
        }
    }, 
    "msg": "Unregistration of Cohesity Protection Source Complete"
}

```

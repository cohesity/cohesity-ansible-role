# Cohesity Agent Management - Linux

## SYNOPSIS
Ansible Module used to deploy or remove the Cohesity Physical Agent from supported Linux Machines.  When executed in a playbook, the Cohesity Agent installation will be validated and the appropriate state action will be applied.  The most recent version of the Cohesity Agent will be automatically downloaded to the host.

### Requirements
  - A physical or virtual Cohesity system. The modules were developed with Cohesity version 6.1.0
  - Ansible 2.6
  - Python >= 2.6

### Notes
  - Currently, the Ansible Module requires Full Cluster Administrator access.

## SYNTAX

```yaml
- cohesity_agent:
    server: <ip or hostname for cohesity cluster>
    cohesity_admin: <username with cluster level permissions>
    cohesity_password: <password for the selected user>
    validate_certs: <boolean to determine if SSL certificates should be validated>
    state: <state of the Agent>
    service_user: <username underwhich the service will run>
    service_group: <group underwhich the service will be owned>
    create_user: <boolean to determine if the service_user and service_group should be created>
```

## EXAMPLES

```yaml
# Install the current version of the agent on Linux
- cohesity_agent:
    server: cohesity.lab
    cohesity_admin: admin
    cohesity_password: password
    state: present

# Install the current version of the agent with custom User and Group
- cohesity_agent:
    server: cohesity.lab
    cohesity_admin: admin
    cohesity_password: password
    state: present
    service_user: cagent
    service_group: cagent
    create_user: True

# Removes the current installed agent from the host
- cohesity_agent:
    server: cohesity.lab
    cohesity_admin: admin
    cohesity_password: password
    state: absent

```


## PARAMETERS

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **cluster** | String | | IP or FQDN for the Cohesity Cluster |
| X | **cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity Cluster |
| X | **cohesity_password** | String | | Password belonging to the selected Username.  This parameter will not be logged. |
|   | validate_certs | Boolean | False | Switch determines if SSL Validation should be enabled. |
|   | state | Choice | -**present**<br>-absent | Determines if the agent should be *present* or *absent* from the host |
|   | service_user | String | cohesityagent | Username underwhich the Cohesity Agent will be installed and run. This user must exist unless *create_user=**True*** is also configured. |
|   | service_group | String | cohesityagent | Group underwhich permissions will be configured for the Cohesity Agent configuration. This group must exist unless *create_user=**True*** is also configured. |
|   | create_user | Boolean | True | When enabled, will create a new user and group based on the values of *service_user* and *service_group*. |


## OUTPUTS
- N/A


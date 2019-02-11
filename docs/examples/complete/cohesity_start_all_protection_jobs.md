# Start All Registered Cohesity Protection Jobs

## Table of Contents
- [Synopsis](#synopsis)
- [Ansible Variables](#ansible-variables)
- [Working with the cohesity_facts Module](#Working-with-the-cohesity_facts-Module)
- [Customize Your Playbooks](#Customize-your-playbooks)
  - [Find and start all registered Protection Jobs](#Find-and-Start-All-Registered-Protection-Jobs)

## Synopsis
[top](#Start-All-Registered-Cohesity-Protection-Jobs)

This example play shows how to use information collected by the *cohesity_facts* module to discover all registered Protection Jobs and start each backup automatically.

#### How It Works
- The play starts by reading all data about the Cohesity cluster and registering a new variable.
- For each registered Protection Job, a call is made to start the backup.

> **Note:**<br>
This play does not require that the Protection Jobs were created via the Ansible Integration as it discovers **all** active Protection Jobs registered in the cluster.

### Requirements
[top](#Start-All-Registered-Cohesity-Protection-Jobs)

  - A physical or virtual Cohesity system. The modules were developed with Cohesity version 6.1.0
  - Ansible version 2.6 or higher
  - Python version 2.6 or higher

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Before using this playbook, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

## Ansible Variables
[top](#Start-All-Registered-Cohesity-Protection-Jobs)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **var_cohesity_server** | String | | IP or FQDN for the Cohesity cluster |
| X | **var_cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity cluster |
| X | **var_cohesity_password** | String | | Password belonging to the selected Username.  This parameter is not logged. |
|   | var_validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |

## Working with the cohesity_facts Module
[top](#Start-All-Registered-Cohesity-Protection-Jobs)

This play leverages certain data collected as part of the `cohesity_facts` module distributed with the Cohesity Ansible Role.  For more information, see [Cohesity Facts](../../modules/cohesity_facts.md).

## Customize Your Playbooks
[top](#Start-All-Registered-Cohesity-Protection-Jobs)

### Find and start all registered Protection Jobs

This is an example playbook that queries the Cohesity cluster for all Protection Jobs that are currently registered and then sends calls to launch each job. The source file for this playbook is located at the root of the role in `examples/complete/cohesity_sart_all_protection_jobs.yml`.  (Remember to change it to suit your environment.)

```yaml
# => Cohesity Protection Job start for all registered Jobs
# =>
# => Role: cohesity.cohesity_ansible_role
# => Version: 0.6.0
# => Date: 2018-12-28
# =>

# => Find and start all active Cohesity Protection Jobs registered to a Cluster
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
      - cohesity.cohesity_ansible_role
    tasks:
        # => Gather Cohesity Facts
        - name: Gather Cohesity Cluster Details
          cohesity_facts:
              cluster: "{{ var_cohesity_server }}"
              username: "{{ var_cohesity_admin }}"
              password: "{{ var_cohesity_password }}"
              validate_certs: "{{ var_validate_certs }}"
              state: minimal
              include_jobs: True
          register: cohesity

        - name: "Cohesity Protection Job: Modify Job to state of started."
          include_role:
            name: cohesity.cohesity_ansible_role
            tasks_from: job
          vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_protection:
                state: started
                job_name: "{{ item['name'] }}"
                environment: "{{ item['environment'].lstrip('k') }}"
          with_items: "{{ cohesity['cluster']['protection']['jobs'] }}"
          tags: [ 'cohesity', 'jobs', 'started' ]
```

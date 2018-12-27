# Cohesity stop all active Protection Jobs

## Table of Contents
- [Synopsis](#synopsis)
- [Ansible Variables](#ansible-variables)
- [Ansible Inventory Configuration](#Ansible-Inventory-Configuration)
- [Working with Cohesity Facts module](#Working-with-Cohesity-Facts-module)
- [Customizing your playbooks](#Customizing-your-playbooks)
  - [Find and cancel active backup jobs](#Find-and-cancel-active-backup-jobs)

## SYNOPSIS
[top](#Cohesity-stop-all-active-Protection-Jobs)

This example play provides an example on how to leverage information collected using the *cohesity_facts* module to automatically discover all currently active protection jobs and cancel each backup.  This source file for this playbook is located at the root of the role in `examples/complete/cohesity_cancel_all_active_jobs.yml`
> **IMPORTANT**!<br>
  This example play should be considered for demo purposes only.  This will cancel **all** actively running backupson an existing Cohesity Cluster

#### How it works 
- The play will start by reading all data about the Cohesity Cluster and registering a new variable.
- For each active Protection Job, a call will be made to cancel the backup.

> **Note**<br>
This play does not require that the jobs were created via the Ansible Integration as it will discover **all** active backup jobs registered in the cluster.

### Requirements
[top](#Cohesity-stop-all-active-Protection-Jobs)

  - A physical or virtual Cohesity system. The modules were developed with Cohesity version 6.1.0
  - Ansible 2.6
  - Python >= 2.6

> **Notes**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Prior to using this playbook, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.

## Ansible Variables
[top](#Cohesity-stop-all-active-Protection-Jobs)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **var_cohesity_server** | String | | IP or FQDN for the Cohesity Cluster |
| X | **var_cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity Cluster |
| X | **var_cohesity_password** | String | | Password belonging to the selected Username.  This parameter will not be logged. |
|   | var_validate_certs | Boolean | False | Switch determines if SSL Validation should be enabled. |

## Working with Cohesity Facts module
[top](#Cohesity-stop-all-active-Protection-Jobs)

This play leverages certain data collected as part of the `cohesity_facts` module distributed with the Cohesity.Ansible Role.  For more information [see our Guide on Cohesity Facts](modules/cohesity_facts.md)

## Customizing your playbooks
[top](#Cohesity-stop-all-active-Protection-Jobs)

### Find and cancel active backup jobs

Here is an example playbook that queries the Cohesity Cluster for all backup jobs that are currently active and then cancels the job. The source file for this playbook is located at the root of the role in `examples/complete/cohesity_cancel_all_active_jobs.yml`.  Please change it as per your environment.

```yaml
# => Cohesity Protection Job cancellation for all active Jobs
# =>
# => Role: cohesity.ansible
# => Version: 0.6.0
# => Date: 2018-12-28
# =>

# => Find and cancel all active Cohesity Protection Jobs registered to a Cluster
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
        # => Gather Cohesity Facts
        - name: Gather Cohesity Cluster Details
          cohesity_facts:
              cluster: "{{ var_cohesity_server }}"
              username: "{{ var_cohesity_admin }}"
              password: "{{ var_cohesity_password }}"
              validate_certs: "{{ var_validate_certs }}"
              state: minimal
              include_runs: True
              active_only: True
          register: cohesity

        - name: "Cohesity Protection Job: Modify Job to state of stopped/canceled."
          include_role:
            name: cohesity.ansible
            tasks_from: job
          vars:
            cohesity_server: "{{ var_cohesity_server }}"
            cohesity_admin: "{{ var_cohesity_admin }}"
            cohesity_password: "{{ var_cohesity_password }}"
            cohesity_validate_certs: "{{ var_validate_certs }}"
            cohesity_protection:
                state: stopped
                job_name: "{{ item['jobName'] }}"
                environment: "{{ item['backupRun']['environment'].lstrip('k') }}"
                cancel_active: True
          with_items: "{{ cohesity['cluster']['protection']['runs'] }}"
          tags: [ 'cohesity', 'jobs', 'stopped' ]
```
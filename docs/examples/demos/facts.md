# Cohesity Facts Collection

## Table of Contents
- [Synopsis](#synopsis)
- [Ansible Inventory Configuration](#Ansible-Inventory-Configuration)
- [Ansible Variables](#ansible-variables)
- [Using the cohesity_facts demo playbook](#Using-the-cohesity_facts-demo-playbook)

## SYNOPSIS
[top](#Cohesity-Facts-Collection)

This example play leverages the `cohesity_facts` module to dynamically discover and store all collected information about a Cohesity Cluster.
Items Collected:
- Cluster Details
- Current Nodes
- All Current Protection Sources
- All Current Protection Jobs
- Protection Policies
- Storage Domains
- Job Execution History for each Current Protection Job

Upon completion of this play, the output will be written into a file called `cohesity_facts.json` and stored in the Ansible Inventory Directory.

> **Note:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Prior to using this playbook, refer to the [Setup](/setup.md) and [How to use](/how-to-use.md) sections of this guide.

## Ansible Inventory Configuration
[top](#cohesity-agent-uninstallation-and-installation-using-ansible-inventory)

To fully leverage this Ansible Play, you must configure your Ansible Inventory file with certain keys and values. This allows for a much easier management of the overall experience.

Here is an example inventory file. Please change it as per your environment.
```ini
[workstation]
control ansible_connection=local ansible_host=10.2.46.94 type=Linux
```

## Ansible Variables
[top](#Cohesity-Facts-Collection)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **var_cohesity_server** | String | | IP or FQDN for the Cohesity Cluster |
| X | **var_cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity Cluster |
| X | **var_cohesity_password** | String | | Password belonging to the selected Username.  This parameter will not be logged. |
|   | var_validate_certs | Boolean | False | Switch determines if SSL Validation should be enabled. |


## Using the cohesity_facts demo playbook
[top](#Cohesity-Facts-Collection)

This source file for this playbook is located at the root of the role in `examples/demos/facts.yml`
```yaml
# => Cohesity Facts saved to JSON file
# =>
# => Role: cohesity.ansible
# => Version: 0.5.0
# => Date: 2018-11-05
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
      - cohesity.ansible
    tasks:
        # => Gather Cohesity Facts
        - name: Gather Cohesity Cluster Details
          cohesity_facts:
              cluster: "{{ var_cohesity_server }}"
              username: "{{ var_cohesity_admin }}"
              password: "{{ var_cohesity_password }}"
              validate_certs: "{{ var_validate_certs }}"
              state: complete
              include_deleted: False
          register: cohesity

        - name: "Write the Collected Facts to {{ inventory_dir }}/cohesity_facts.json"
          local_action: copy content="{{ cohesity | to_nice_json }}" dest="{{ inventory_dir }}/cohesity_facts.json"
```

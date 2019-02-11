# Cohesity Facts Collection

## Table of Contents
- [Synopsis](#synopsis)
- [Ansible Inventory Configuration](#Ansible-Inventory-Configuration)
- [Ansible Variables](#ansible-variables)
- [Using the cohesity_facts Demo Playbook](#Using-the-cohesity_facts-demo-playbook)

## Synopsis
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

Upon completion of this play, the output is written to a file called `cohesity_facts.json` and stored in the Ansible Inventory Directory.

> **Note:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - Prior to using this playbook, refer to the [Setup](../../setup.md) and [How to Use](../../how-to-use.md) sections of this guide.

## Ansible Inventory Configuration
[top](#Cohesity-Facts-Collection)

To fully leverage this Ansible Play, you must configure your Ansible Inventory file with certain keys and values. This makes it much easier to manage the overall experience. See [Configure Your Ansible Inventory](../configuring-your-ansible-inventory.md).

This is an example inventory file: (Remember to change it to suit your environment.)
```ini
[workstation]
control ansible_connection=local ansible_host=10.2.46.94 type=Linux
```

## Ansible Variables
[top](#Cohesity-Facts-Collection)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **var_cohesity_server** | String | | IP or FQDN for the Cohesity cluster |
| X | **var_cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity cluster |
| X | **var_cohesity_password** | String | | Password belonging to the selected Username.  This parameter is not logged. |
|   | var_validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |


## Using the cohesity_facts Demo Playbook
[top](#Cohesity-Facts-Collection)

The source file for this playbook is located at the root of the role in `examples/demos/facts.yml`.

```yaml
# => Cohesity Facts saved to JSON file
# =>
# => Role: cohesity.cohesity_ansible_role
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
      - cohesity.cohesity_ansible_role
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

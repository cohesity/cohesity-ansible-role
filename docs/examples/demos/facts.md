# Cohesity Facts Collection

## SYNOPSIS
This example play leverages the `cohesity_facts` module to dynamically discover and store all collected information about a Cohesity cluster.
Items collected:
- Cluster Details
- Current Nodes
- All Current Protection Sources
- All Current Protection Jobs
- Protection Policies
- Storage Domains
- Job Execution History for each Current Protection Job

Upon completion of this play, the output is written to a file called `cohesity_facts.json` and stored in the Ansible Inventory Directory.

> **Tip:**  Currently, the Ansible Module requires Full Cluster Administrator access.

## Ansible Variables

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **var_cohesity_server** | String | | IP or FQDN for the Cohesity cluster |
| X | **var_cohesity_admin** | String | | Username with which Ansible will connect to the Cohesity Cluster |
| X | **var_cohesity_password** | String | | Password belonging to the selected Username.  This parameter is not logged. |
|   | var_validate_certs | Boolean | False | Switch that determines whether SSL Validation is enabled. |


# Cohesity Ansible Role Documentation

Refer the Cohesity Ansible Role Documentation here. The documentation covers different modules in the library, tasks for all these modules and some sample playbooks to get started. 

## Table of contents :scroll:

- [Getting Started](#get-started)
- [Modules](#modules)
- [Tasks](#tasks)
- [Examples](#example)
- [Suggestions and Feedback](#suggest)

## <a name="get-started"></a> Let's get started :hammer_and_pick:

- [Introduction](./common/overview.md)
- [Prerequisites](./common/pre-requisites.md)
- [Setup](./common/setup.md)
- [How to use](./common/how-to-use.md)
- [Configure your Ansible Inventory](./common/configuring-your-ansible-inventory.md)
- [Feedback](./common/feedback.md)


## <a name="modules"></a> Available modules 

- [cohesity_facts](./library/cohesity_facts.md)
- [cohesity_agent](./library/cohesity_agent.md)
- [cohesity_win_agent](./library/cohesity_win_agent.md)
- [cohesity_source](./library/cohesity_source.md)
- [cohesity_job](./library/cohesity_job.md)
- [cohesity_restore_file](./library/cohesity_restore_file.md)
- [cohesity_restore_vm](./library/cohesity_restore_vm.md)

## <a name="tasks"></a> Taks for each module

- [agent](./tasks/agent.md)
- [win_agent](./tasks/win_agent.md)
- [source](./tasks/source.md)
- [job](./tasks/job.md)
- [restore_file](./tasks/restore_file.md)
- [restore_vm](./tasks/restore_vm.md)


## <a name="example"></a> Examples to get you started :bulb:

- [Demo: Collect Facts](./examples/facts.md)
- [Demo: Agent Management](./examples/agents.md)
- [Demo: Source Management](./examples/sources.md)
- [Demo: Job Management](./examples/jobs.md)
- [Advanced: Protect All Hosts in Inventory](./examples/cohesity_protect_inventory)
- [Advanced: Start All Registered Jobs](./examples/cohesity_start_all_protection_jobs.md)
- [Advanced: Stop All Active Jobs](./examples/cohesity_stop_all_active_protection_jobs.md)

For more sample playbooks refer our playbooks folder.

## <a name="suggest"></a> Suggestions and Feedback :raised_hand:

We would love to hear from you. Please send your suggestions and feedback to: [cohesity-api-sdks@cohesity.com](mailto:cohesity-api-sdks@cohesity.com)


# Cohesity Policy Management

[Go back to Documentation home page ](../README.md)

## Table of Contents
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Syntax](#syntax)
- [Examples](#examples)
  - Policy Management
    - [Create a Protection Policy](#Create-a-Protection-Policy)
    - [Delete a Protection Policy](#Delete-a-Protection-Policy)
- [Parameters](#parameters)
- [Parameters sub option](#parameters-sub-option)
- [Outputs](#outputs)

## Synopsis
[top](#cohesity-policy-management)

The Ansible Module creates or deletes a Protection Policy for the Cohesity Cluster

### Requirements
[top](#cohesity-policy-management)

* Cohesity DataPlatform running version 6.3 or higher
* Ansible version 2.6 or higher
  * The [Ansible Control Machine](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#control-machine-requirements) must be a system running one of the following UNIX operating systems: Linux (Red Hat, Debian, CentOS), macOS, or any of the BSDs. Windows is not supported for the Control Machine.
* Python version 2.6 or higher

> **Notes:**
  - Currently, the Ansible Module requires Full Cluster Administrator access.
  - When using the default download location, the Cohesity agent installer is placed in `/tmp/<temp-dir`.  If your environment prevents the use of `/tmp` with a `noexec` option, then you must set an alternate location.

## Syntax
[top](#cohesity-policy-management)

```yaml
- cohesity_policy:
    cluster: <ip or hostname for cohesity cluster>
    username: <cohesity username with cluster level permissions>
    password: <cohesity password for the selected user>
    validate_certs: <boolean to determine if SSL certificates should be validated>
    name: <Name of the Protection Policy>
    description: <Protection Policy Description>
    state: <Determines if the Protection Policy should be present or absent from the host>
    days_to_retain: <Retains backup or 'days_to_retain' number of days>
    incremental_backup_schedule: <Specify the incremental backup schedule in Protection Policy>
    full_backup_schedule: <Specify the full backup schedule>
    blackout_window: <Specify the blackout window for retries> 
    retries: <Specifies the number of times to retry capturing Snapshots if the Job Run fails.>
    retry_interval: <Specifies the number of minutes before retrying a failed Protection Job>
    bmr_backup_schedule: <Specify the BMR backup schedule for the Protection Policy> 
    log_backup_schedule: <Specify the Log Backup for the Protection Policy> 
    extended_retention: <Specify the Extended schedule for the Protection Policy> 
    archival_copy: <Specify the Archival details for the Protection Policy> 
```

## Examples
[top](#cohesity-policy-management)

### Create a Protection Policy
[top](#cohesity-policy-management)

```yaml
- cohesity_policy:
    name: POLICY_NAME
    incremental_backup_schedule:   
      periodicity: Daily
      days: 
        - Monday
        - Tuesday
    cluster: cohesity.lab
    username: admin
    password: password
    state: present
```

### Delete a Protection Policy
[top](#cohesity-policy-management)

```yaml
- cohesity_policy:
    name: POLICY_NAME
    incremental_backup_schedule:   
      periodicity: Daily
      days: 
        - Monday
        - Tuesday
    cluster: cohesity.lab
    username: admin
    password: password
    state: absent
```

## Parameters
[top](#cohesity-policy-management)

| Required | Parameters | Type | Choices/Defaults | Comments |
| --- | --- | --- | --- | --- |
| X | **name** | String | | Name of the Protection Policy. |
|  | description | String | | Protection Policy Description.|
|  | state | Choice | -**present**<br>-absent | Determines if the Protection Policy should be present or absent from the host.|
|  | days_to_retain | Integer | 30 | Retains backup or 'days_to_retain' number of days.|
| X | [**incremental_backup_schedule**](#incremental_backup_schedule) | dict | | Specify the incremental backup schedule in Protection Policy.|
|   | [full_backup_schedule](#full_backup_schedule) | dict | False |  |
|   | [blackout_window](#blackout_window) | dict | False | Specify the blackout window for retries. |
|   | retries | Choice | -**present**<br>-absent | Determines whether the agent is *present* or *absent* from the host. |
|   | retry_interval | Integer | | Specify the retry_interval value for retries.|
|   | [bmr_backup_schedule](#bmr_backup_schedule) | dict | | Specify the BMR backup schedule for the Protection Policy.|
|   | [log_backup_schedule](#log_backup_schedule) | dict | | Specify the Log Backup for the Protection Policy.|
|   | [extended_retention](#extended_retention) | List | | Specify the Extended schedule for the Protection Policy.|
|   | [archival_copy](#archival_copy) | List | | Specify the Archival details for the Protection Policy.|

## Parameters sub option
[top](#cohesity-policy-management)

#### <a name="incremental_backup_schedule"></a> incremental_backup_schedule: 

This option is of type `dict` and has the following Keys

  * #### periodicity 

    **Type** : `String`

    **Required**: `True`
    
    **Description**:  Specifies how often to start new Job Runs of a Protection Job. `Daily` For daily or weekly schedule `Monthly` for monthly schedule `Continuous` means new Job Runs repetitively start at the beginning of the specified time interval.

    - If periodicity is `Daily`, specify

      - `days` 

        **Type** : `List of strings`
        
        **Description**: Specifies a list of days of the week when to start Job Runs. If no days are specified, the Jobs Runs will run every day of the week. Specifies days in a week such as 'Sunday', 'Monday', etc.

    - If periodicity is `Monthly`, specify

      - `day`

        **Type** : `String`

        **Required**: `True`
        
        **Description**: Specifies the day of the week (such as 'Monday' *Case Sensitive*) to start the Job Run. Used with day count to define the day in the month to start     the Job Run. Specifies a day in a week such as 'Sunday', 'Monday', etc.

      - `day_count`

        **Type** : `String`

        **Required**: `True`
        
        **Description**: Specifies the day count in the month (such as 'Third' *Case Sensitive*) to start the Job Run. Used in combination with day to define the day in the month to start the Job Run. Specifies the day count in the month to start the backup. For example if day count is set to 'Third' and day is set to 'Monday', a backup is performed on the third Monday of every month. 'First' indicates that the first week should be choosen for specified day of every month. 'Second' indicates that the second week should be choosen for specified day of every month. 'Third' indicates that the third week should be choosen for specified day of every month. 'Fourth' indicates that the fourth week should be choosen for specified day of every month. 'Last' indicates that the last week should be choosen for specified day of every month.
  
    - If periodicity is `Continuous`, specify

      - `backup_interval_mins`

        **Type** : `Integer`

        **Required**: `True`
        
        **Description**: this field defines the time interval in minutes when new Job Runs are started.

#### <a name="full_backup_schedule"></a> full_backup_schedule: 

  This option is of type `dict` and has the following Keys

  * #### periodicity 

    **Type** : `String`

    **Required**: `True`
    
    **Description**:  Specifies how often to start new Job Runs of a Protection Job. `Daily` For daily or weekly schedule `Monthly` for monthly schedule `Continuous` means new Job Runs repetitively start at the beginning of the specified time interval.

    - If periodicity is `Daily`, specify

      - `days` 

        **Type** : `List of strings`
        
        **Description**: Specifies a list of days of the week when to start Job Runs. If no days are specified, the Jobs Runs will run every day of the week. Specifies days in a week such as 'Sunday', 'Monday', etc.

    - If periodicity is `Monthly`, specify

      - `day`

        **Type** : `String`

        **Required**: `True`
        
        **Description**: Specifies the day of the week (such as 'Monday' *Case Sensitive*) to start the Job Run. Used with day count to define the day in the month to start     the Job Run. Specifies a day in a week such as 'Sunday', 'Monday', etc.

      - `day_count`

        **Type** : `String`

        **Required**: `True`
        
        **Description**: Specifies the day count in the month (such as 'Third' *Case Sensitive*) to start the Job Run. Used in combination with day to define the day in the month to start the Job Run. Specifies the day count in the month to start the backup. For example if day count is set to 'Third' and day is set to 'Monday', a backup is performed on the third Monday of every month. 'First' indicates that the first week should be choosen for specified day of every month. 'Second' indicates that the second week should be choosen for specified day of every month. 'Third' indicates that the third week should be choosen for specified day of every month. 'Fourth' indicates that the fourth week should be choosen for specified day of every month. 'Last' indicates that the last week should be choosen for specified day of every month.

#### <a name="blackout_window"></a> blackout_window: 

  This option is a List of dictionaries. Keys in the dictionary are:

  * #### day 

    **Type** : `String`

    **Default**: `Wednesday`
    
    **Description**:  Blackout Day.Specifies a day in the week when no new Job Runs should be started such as `Sunday`. Possible options are Sunday, Monday, Tuesday, Wednesday, Thursday, Friday

  * #### start_time 

    **Type** : `String`

    **Default**: `12:00`
    
    **Description**:  Specifies the start time of the blackout time range. Specified in 24 hr format, example `14:30`, `23:45`..

  * #### end_time 

    **Type** : `String`

    **Default**: `12:30`
    
    **Description**:  string, defaults to ‘12:30’. Specifies the end time of the blackout time range. Specified in 24 hr format, example `11:30`, `15:45`..

#### <a name="bmr_backup_schedule"></a> bmr_backup_schedule: 

  This option is of type dict. Keys in the dictionary are:

  * #### days_to_retain 

    **Type** : `Integer`

    **Required**: `True`
    
    **Description**:  Specifies the number of days to retain system backups made for bare metal recovery. This field is applicable if `systemSchedulingPolicy` is specified.

  * #### periodicity 

    **Type** : `String`

    **Required**: `True`
    
    **Description**:  Specifies how often to start new Job Runs of a Protection Job. `Daily` For daily or weekly schedule `Monthly` for monthly schedule `Continuous` means new Job Runs repetitively start at the beginning of the specified time interval.

    - If periodicity is `Daily`, specify

      - `days` 

        **Type** : `List of strings`
        
        **Description**: Specifies a list of days of the week when to start Job Runs. If no days are specified, the Jobs Runs will run every day of the week. Specifies days in a week such as 'Sunday', 'Monday' (*Case Sensitive*) etc.

    - If periodicity is `Monthly`, specify

      - `day`

        **Type** : `String`

        **Required**: `True`
        
        **Description**: Specifies the day of the week (such as 'Monday' *Case Sensitive*) to start the Job Run. Used with day count to define the day in the month to start     the Job Run. Specifies a day in a week such as 'Sunday', 'Monday', etc.

      - `day_count`

        **Type** : `String`

        **Required**: `True`
        
        **Description**: Specifies the day count in the month (such as 'Third' *Case Sensitive*) to start the Job Run. Used in combination with day to define the day in the month to start the Job Run. Specifies the day count in the month to start the backup. For example if day count is set to 'Third' and day is set to 'Monday', a backup is performed on the third Monday of every month. 'First' indicates that the first week should be choosen for specified day of every month. 'Second' indicates that the second week should be choosen for specified day of every month. 'Third' indicates that the third week should be choosen for specified day of every month. 'Fourth' indicates that the fourth week should be choosen for specified day of every month. 'Last' indicates that the last week should be choosen for specified day of every month.

#### <a name="log_backup_schedule"></a> log_backup_schedule: 

  This option is of type dict. Keys in the dictionary are:

  * #### days_to_retain 

    **Type** : `Integer`

    **Required**: `True`
    
    **Description**:  Specifies the number of days to retain log run if Log Schedule exists.

  * #### periodicity 

    - If periodicity is `Continuous`, specify

      - `backup_interval_mins`

        **Type** : `Integer`

        **Required**: `True`
        
        **Description**: this field defines the time interval in minutes when new Job Runs are started.

#### <a name="extended_retention"></a> extended_retention: 

  This option is a List of dictionaries. Keys in the dictionary are:

  * #### backup_run_type 

    **Type** : `String`

    **Required**: `True`
    
    **Description**:  The backup run type to which this extended retention applies to. If this is not set, the extended retention will be applicable to all non-log backup types. Currently, the only value that can be set here is kFull. 'Regular' indicates a incremental (CBT) backup. Incremental backups utilizing CBT (if supported) are captured of the target protection objects. The first run of a kRegular schedule captures all the blocks. 'Full' indicates a full (no CBT) backup. A complete backup (all blocks) of the target protection objects are always captured and Change Block Tracking (CBT) is not utilized. 'Log' indicates a Database Log backup. Capture the database transaction logs to allow rolling back to a specific point in time. 'System' indicates a system backup. System backups are used to do bare metal recovery of the system to a specific point in time.

  * #### retention_periodicity 

    **Type** : `String`

    **Description**:  Specifies the frequency that Snapshots should be copied to the specified target. Used in combination with multipiler. 'Every' means that the Snapshot copy occurs after the number of Job Runs equals the number specified in the multiplier. 'Hour' means that the Snapshot copy occurs hourly at the frequency set in the multiplier, for example if multiplier is 2, the copy occurs every 2 hours. 'Day' means that the Snapshot copy occurs daily at the frequency set in the multiplier. 'Week' means that the Snapshot copy occurs weekly at the frequency set in the multiplier. 'Month' means that the Snapshot copy occurs monthly at the frequency set in the multiplier. 'Year' means that the Snapshot copy occurs yearly at the frequency set in the multiplier.

  * #### multiplier 

    **Type** : `Integer`

    **Default**: `1`
    
    **Description**:  Specifies a factor to multiply the periodicity by, to determine the copy schedule. For example if set to 2 and the periodicity is hourly, then Snapshots

  * #### days_to_retain 

    **Type** : `Integer`

    **Required**: `True`
    
    **Description**:  Specifies the number of days to retain copied Snapshots on the target.

#### <a name="archival_copy"></a> archival_copy: 

  This option is a List of dictionaries. Keys in the dictionary are:

  * #### multiplier 

    **Type** : `Integer`

    **Default**: `1`

    **Description**:  Specifies a factor to multiply the periodicity by, to determine the copy schedule. For example if set to 2 and the periodicity is hourly, then Snapshots from the first eligible Job Run for every 2 hour period is copied.

  * #### copy_partial 

    **Type** : `Boolean`

    **Default**: `True`
    
    **Description**:  Specifies if Snapshots are copied from the first completely successful Job Run or the first partially successful Job Run occurring at the start of the replication schedule. If true, Snapshots are copied from the first Job Run occurring at the start of the replication schedule, even if first Job Run was not completely successful i.e. Snapshots were not captured for all Objects in the Job. If false, Snapshots are copied from the first Job Run occurring at the start of the replication schedule that was completely successful i.e. Snapshots for all the Objects in the Job were successfully captured.

  * #### days_to_retain 

    **Type** : `Integer`

    **Default**: `whatever is given for incremental backup`
    
    **Description**:  Specifies the number of days to retain copied Snapshots on the target.

  * #### periodicity 

    **Type** : `String`

    **Required**: `Day`
    
    **Description**:  Specifies the frequency that Snapshots should be copied to the specified target. Used in combination with multipiler. 'Every' means that the Snapshot copy occurs after the number of Job Runs equals the number specified in the multiplier. 'Hour' means that the Snapshot copy occurs hourly at the frequency set in the multiplier, for example if multiplier is 2, the copy occurs every 2 hours. 'Day' means that the Snapshot copy occurs daily at the frequency set in the multiplier. 'Week' means that the Snapshot copy occurs weekly at the frequency set in the multiplier. 'Month' means that the Snapshot copy occurs monthly at the frequency set in the multiplier. 'Year' means that the Snapshot copy occurs yearly at the frequency set in the multiplier.

  * #### target_name 

    **Type** : `String`

    **Required**: `True`
    
    **Description**:  Name of the Archival Vault.

  * #### days_to_retain 

    **Type** : `String`

    **Required**: `True`
    
    **Description**:  Specifies the type of the Archival External Target such as 'Cloud', 'Tape' or 'Nas'. 'Cloud' indicates the archival location as Cloud. 'Tape' indicates the archival location as Tape. 'Nas' indicates the archival location as Network Attached Storage (Nas).


## Outputs
[top](#cohesity-policy-management)
- N/A


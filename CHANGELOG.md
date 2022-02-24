# Cohesity Ansible Changelog

## Version v2.3.4
  Date:   Thu Feb 24 2022
    UPDATE:   Added support to provide interface group name, network name
              and folder name while Restoring VM.
    UPDATE:   User authentication fix for MT, AD user support.
    UPDATE:   Documentation update

## Version 0.4.0
  Date:   Tue Oct 30 2018
    ADD:    Gitbook Documentation
    ADD:    Example Play Files and Demos
    ADD:    LICENSE
    ADD:    CHANGELOG
    ADD:    README
    UPDATE: Modules Ansible native Documentation
    UPDATE: Pylint validations
    UPDATE: PEP8 and SHEBANG tests

## Version 0.3.0
  Date:   Tue Oct 16 2018
    ADD:    Tasks::Sources to streamline the creation of supported Cohesity Sources
    ADD:    Tasks::Jobs to streamline the creation of supported Cohesity Protection Jobs
    ADD:    Tasks::WinAgent to install and manage Cohesity Agent on Windows Servers
    ADD:    Module::CohesityJob to create and manage Protection Jobs
    ADD:    Module::CohesitySource to register and remove Protection Sources
    ADD:    Unit::Tests::CohesityJob
    ADD:    Unit::Tests::CohesitySource
    ADD:    ModuleUtils::CohesityHelper to include helper methods for gathering and filtering data from Cohesity
    UPDATE: Module::CohesityAgent refactored to use the updated format
    UPDATE: Module::CohesityFacts to include new hints and information
    UPDATE: ModuleUtils::CohesityAuth include new helper function get__cohesity_auth__token
    UPDATE: Util::DocFragent::Cohesity with default arguments

## Version 0.2.0
  Date:   Wed Oct 10 2018
    ADD:    Module::CohesityAgent for Linux installations
    ADD:    Module::CohesityWinAgent for Windows installations
    ADD:    Task::agent example to install agent on Linux
    ADD:    Defaults::main with default variables
    ADD:    Spec::CohesityAgent

## Version 0.1.0
  Date:   Sep 29 2018
    ADD:    Initial scaffold for Role
    ADD:    Initial model for CohesityAuth module_utility
    ADD:    UnitTest::CohesityAuth
    ADD:    Initial Cohesity::Authentication class and tests
    ADD:    CohesityFacts Module
    ADD:    PEP8 validation

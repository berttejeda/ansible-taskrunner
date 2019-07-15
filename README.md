<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Overview](#overview)
- [Use case and example](#use-case-and-example)
  - [Given](#given)
  - [Task](#task)
  - [Investigation](#investigation)
  - [Assessment](#assessment)
  - [Proposed Solution](#proposed-solution)
- [Technical Details](#technical-details)
  - [Add hosts designation](#add-hosts-designation)
  - [Add vars key](#add-vars-key)
  - [Populate the vars block - defaults](#populate-the-vars-block---defaults)
  - [Populate the vars block - cli options](#populate-the-vars-block---cli-options)
    - [Populate the vars block - cli options - mapped variables](#populate-the-vars-block---cli-options---mapped-variables)
  - [Populate the vars block - help/message](#populate-the-vars-block---helpmessage)
  - [Populate the vars block - inventory](#populate-the-vars-block---inventory)
  - [Populate the vars block - internal functions](#populate-the-vars-block---internal-functions)
  - [Add tasks](#add-tasks)
- [Usage Examples](#usage-examples)
  - [More Examples](#more-examples)
- [Appendix](#appendix)
  - [Special Variables](#special-variables)
    - [ansible_playbook_command](#ansible_playbook_command)
    - [parameter_set](#parameter_set)
  - [Single-Executable Releases](#single-executable-releases)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<a name="overview"></a>
# Overview

This is a task runner that serves as a higher-level automation layer to ansible

The script expects an ansible-playbook file as the task manifest.

By default, this is a file named 'Taskfile.yaml' in the current working directory.

The inspiration for the tool comes from the gnu make command, which operates in similar fashion, i.e.

- A Makefile defines available build steps
- The make command consumes the Makefile at runtime and exposes these steps as commandline options

<a name="use-case-and-example"></a>
# Use case and example

<a name="given"></a>
## Given

1. An enterprise-grade application named contoso-app
2. Multiple teams:
- Development
- Engineering
- DBA
- Operations
- QA
3. Ansible is the primary means of invoking business and operational processes across the numerous environment(s)

<a name="task"></a>
## Task

You must ensure all teams adopt a standardized approach to running ansible workloads

<a name="investigation"></a>
## Investigation

Upon investigating the current approach, you observe the following: 

- Users tend to create wrapper scripts that call the ansible-playbook command
- These scripts don't follow any naming convention, as you've noted:
  - run.sh
  - start.sh
  - playbook.sh
- These shell scripts have common attributes:
  - Dynamically populate ansible-playbook variables via the --extra-vars option
  - Dynamically creating ansible inventories
  - Performing pre/post-flight tasks
  - Providing a command-line interface

<a name="assessment"></a>
## Assessment

Advantages to the above approach:
- Quick-n-dirty, anyone can get started relatively quickly with writing ansible automation

Disadvantages:
- Lack of standards: 
- Leads to difficulty in collaboration and code refactoring
- Decreased re-usability of codebase
  - This design encourages standalone playbooks
  - Duplicate efforts across codebase

<a name="proposed-solution"></a>
## Proposed Solution

Create ansible task runner that reads a specially formatted ansible playbook (Taskfile.yaml)
  - Accomplishes the same as the above, but in more uniform manner
  - Each tasks playbook behaves like a commandline script
  - Support for commandline parameters/flags
  - Embedded dynamic inventory
  - Internal shell functions

Advantages to this approach:
- Easier to manage
  - If you know YAML and Ansible, you can get started relatively quickly with writing ansible automation
- Single executable (/usr/local/bin/tasks)

Disadvantages:
- Target ansible controller needs to have the command installed

<a name="technical-details"></a>
# Technical Details

This tool functions much like the *make* command in that it accepts an input file that essentially extends its cli options.

We create a specially formatted ansible-playbook that serves as a task definition file (by default, Taskfile.yaml).

In the following sections, we'll be building a sample manifest/playbook named *Taskfile.yaml*

<a name="add-hosts-designation"></a>
## Add hosts designation

<details>
  <summary>Add hosts, gather_facts, etc</summary>

*Taskfile.yaml*

```
- hosts: myhosts
  gather_facts: true
  become: true
```

</details>

<a name="add-vars-key"></a>
## Add vars key

Remember, the task runner will ultimately be calling the `ansible-playbook` command against this very same file, so it must be conformant.

<details>
  <summary>We add the 'vars' key, which allows ansible to populate the variables we are defining in this block.</summary>

*Taskfile.yaml*

```
- hosts: myhosts
  gather_facts: true
  become: true
  vars:
```

</details>

<a name="populate-the-vars-block---defaults"></a>
## Populate the vars block - defaults

<details>
  <summary>Let's add some default variables to the playbook:</summary>

*Taskfile.yaml*

```
- hosts: myhosts
  gather_facts: true
  become: true
  vars:
    myvar1: myvalue1
    myvar2: myvalue2
    myvar3: myvalue3
    myvar4: |
      This is a multi-line value
      of type string
    myvar5:
      - mylistvalue1
      - mylistvalue2
      - mylistvalue3
      - mylistvalue4
```

</details>

<a name="populate-the-vars-block---cli-options"></a>
## Populate the vars block - cli options

<details>
  <summary>Next, we add the cli interface: </summary>

*Taskfile.yaml*

```
- hosts: myhosts
  gather_facts: true
  become: true
  vars:
    myvar1: myvalue1
    myvar2: myvalue2
    myvar3: myvalue3
    myvar4: |
      This is a multi-line value
      of type string
    myvar5:
      - mylistvalue1
      - mylistvalue2
      - mylistvalue3
      - mylistvalue4
    required_parameters:
      -d|--db-hosts: dbhosts
      -w|--web-hosts: webhosts
      -t|--some-parameter: some_value
    optional_parameters:
      -l|--another-parameter: another_value
      -A: hello
      --debug-mode: debug_mode
```   

</details>

Notice the parameter definitions:
  - required_parameters
  - optional_paramters

These are yaml list objects that expose optional and required command-line options.

The syntax for the options is as follows:

`-{{ short_option }}|--{{ long_option }}: {{ mapped_variable }}`

Examples:

```
Options       | Mapped Variable
------------- | -------------
-f|--foo      | some_foo_variable
-b|--bar      | some_bar_variable
-F|--foo-bar  | some_other_variable
-a|--all-else | [remaining_args] (behaves like click's nargs=1)
--some-option | some_switch (behaves like click switches, holds the value of True if specified)
```

More flexibility can be achieved through the use of parameter sets.

See the [appendix](#parameter_set) for more information.

<a name="populate-the-vars-block---cli-options---mapped-variables"></a>
### Populate the vars block - cli options - mapped variables

It's important to note that the above mapped variables can be used during runtime, i.e. referenced in any defined functions, embedded inventory logic, etc.

Consider the `-f|-foo` option above.

Whatever argument you pass to this option becomes the value for the mapped variable.

Again, this variable is made available to the underlying subprocess call, and within the ansible playbook itself.

<a name="populate-the-vars-block---helpmessage"></a>
## Populate the vars block - help/message

<details>
  <summary>Next, we add the help/message section</summary>

*Taskfile.yaml*

```
- hosts: myhosts
  gather_facts: true
  become: true
  vars:
    myvar1: myvalue1
    myvar2: myvalue2
    myvar3: myvalue3
    myvar4: |
      This is a multi-line value
      of type string
    myvar5:
      - mylistvalue1
      - mylistvalue2
      - mylistvalue3
      - mylistvalue4
    required_parameters:
      -d|--db-hosts: dbhosts
      -w|--web-hosts: webhosts
      -t|--some-parameter: some_value
    optional_parameters:
      -l|--another-parameter: another_value
      -A: hello
      --debug-mode: debug_mode
    help:
      message: |
        Do something against db and web hosts
      epilog: |
        This line will be displayed at the end of the help text message
      examples:
        - example1: |
            Usage example 1
        - example2: |
            Usage example 2
```

</details>

<a name="populate-the-vars-block---inventory"></a>
## Populate the vars block - inventory

<details>
  <summary>Add the dynamic inventory section</summary>

*Taskfile.yaml*

```
- hosts: myhosts
  gather_facts: true
  become: true
  vars:
    myvar1: myvalue1
    myvar2: myvalue2
    myvar3: myvalue3
    myvar4: |
      This is a multi-line value
      of type string
    myvar5:
      - mylistvalue1
      - mylistvalue2
      - mylistvalue3
      - mylistvalue4
    required_parameters:
      -d|--db-hosts: dbhosts
      -w|--web-hosts: webhosts
      -t|--some-parameter: some_value
    optional_parameters:
      -l|--another-parameter: another_value
      -A: hello
      --debug-mode: debug_mode
    help:
      message: |
        Do something against db and web hosts
      epilog: |
        This line will be displayed at the end of the help text message
      examples:
        - example1: |
            Usage example 1
        - example2: |
            Usage example 2
    inventory: |
      [web-hosts]
      $(echo ${webhosts} | tr ',' '\\n')
      [db-hosts]
      $(echo ${dbhosts} | tr ',' '\\n')
      [myhosts:children]
      deployment-hosts
      web-hosts
      db-hosts
```

</details>

<a name="populate-the-vars-block---internal-functions"></a>
## Populate the vars block - internal functions

<details>
  <summary>Add internal functions: </summary>

*Taskfile.yaml*

```
- hosts: myhosts
  gather_facts: true
  become: true
  vars:
    myvar1: myvalue1
    myvar2: myvalue2
    myvar3: myvalue3
    myvar4: |
      This is a multi-line value
      of type string
    myvar5:
      - mylistvalue1
      - mylistvalue2
      - mylistvalue3
      - mylistvalue4
    required_parameters:
      -d|--db-hosts: dbhosts
      -w|--web-hosts: webhosts
      -t|--some-parameter: some_value
    optional_parameters:
      -l|--another-parameter: another_value
      -A: hello
      --debug-mode: debug_mode
    help:
      message: |
        Do something against db and web hosts
      epilog: |
        This line will be displayed at the end of the help text message
      examples:
        - example1: |
            Usage example 1
        - example2: |
            Usage example 2
    inventory: |
      [web-hosts]
      $(echo ${webhosts} | tr ',' '\\n')
      [db-hosts]
      $(echo ${dbhosts} | tr ',' '\\n')
      [myhosts:children]
      deployment-hosts
      web-hosts
      db-hosts
    functions:
      hello:
        shell: bash
        source: |-
          echo hello
```

</details>

<a name="add-tasks"></a>
## Add tasks

<details>
  <summary>Finally, we add tasks!</summary>

*Taskfile.yaml*

```
- hosts: myhosts
  gather_facts: true
  become: true
  vars:
    myvar1: myvalue1
    myvar2: myvalue2
    myvar3: myvalue3
    myvar4: |
      This is a multi-line value
      of type string
    myvar5:
      - mylistvalue1
      - mylistvalue2
      - mylistvalue3
      - mylistvalue4
    required_parameters:
      -d|--db-hosts: dbhosts
      -w|--web-hosts: webhosts
      -t|--some-parameter: some_value
    optional_parameters:
      -l|--another-parameter: another_value
      -A: hello
      --debug-mode: debug_mode
    help:
      message: |
        Do something against db and web hosts
      epilog: |
        This line will be displayed at the end of the help text message
      examples:
        - example1: |
            Usage example 1
        - example2: |
            Usage example 2
    inventory: |
      [web-hosts]
      $(echo ${webhosts} | tr ',' '\\n')
      [db-hosts]
      $(echo ${dbhosts} | tr ',' '\\n')
      [myhosts:children]
      deployment-hosts
      web-hosts
      db-hosts
    functions:
      hello:
        shell: bash
        source: |-
          echo hello
  tasks:
    - debug: 
        msg: |
          Hello from Ansible!
          You specified: {{ some_value }}
          You specified: {{ another_value }}
```

</details>

<a name="usage-examples"></a>
# Usage Examples

Quick usage examples:

* Display help for main command
  `release/{{ version }}/tasks --help`
* Display help for the *run* subcommand
  `release/{{ version }}/tasks run --help`
* Don't do anything, just echo the underlying shell command
  `release/{{ version }}/tasks run -d dbhost1 -w webhost1 -t value1 --echo`
  Result should be similar to:
  `ansible-playbook -i C:\Users\${USERNAME}\AppData\Local\Temp\ansible-inventory16xdkrjd.tmp.ini -e dbhosts="dbhost1" -e webhosts="webhost1" -e some_value="value1" -e echo="True" Taskfile.yaml`
* Run the playbook!
  `release/{{ version }}/tasks run -d dbhost1 -w webhost1 -t value1`

Now all you need to do is install the `tasks` binary to your ansible controller to start using this workflow!

<a name="more-examples"></a>
## More Examples

Review the [examples](examples) directory for more hands-on usage samples.

<a name="appendix"></a>
# Appendix

<a name="special-variables"></a>
## Special Variables

<a name="ansible_playbook_command"></a>
### ansible_playbook_command

If you define the playbook variable *ansible_playbook_command*, this will override the underlying ansible-playbook command invocation.

As an example, suppose I define this variable in the above *Taskfile.yaml*, as follows:

```
- hosts: myhosts
  gather_facts: true
  become: true
  vars:
    ansible_playbook_command: 'python ${HOME}/ansible_2.7.8/ansible-playbook'
    myvar1: myvalue1
    myvar2: myvalue2
    myvar3: myvalue3
    # ...
```
Upon invoking the `tasks` command with the `--echo` flag, the underlying shell command would then be revealed as:

`python ${HOME}/ansible_2.7.8/ansible-playbook -i C:\Users\${USERNAME}\AppData\Local\Temp\ansible-inventory16xdkrjd.tmp.ini -e dbhosts="dbhost1" -e webhosts="webhost1" -e some_value="value1" -e echo="True" Taskfile.yaml`

<a name="parameter_set"></a>
### parameter_set

What if you wanted to operate under multiple contexts?

e.g. You want to be able to interact with Amazon Web Services (AWS) and Google Cloud Platform (GCP)?

Sure, you could add paramters to your heart's content, but you'll pollute the output from `--help`

This is where parameter sets come into play.

The functionality is simple. Precede the `run` subcommand with a single word.

This word acts as a _mini_ subcommand, and _unlocks_ the command-line options defined by the corresponding key in the appropriate options section of your manifest.

Here's an example:

```
    required_parameters:
      aws:
        -aws|--some-aws-option: aws_option
      gcp:
        -gcp|--some-gcp-option: gcp_option
      -d|--db-hosts: dbhosts
      -w|--web-hosts: webhosts
      -t|--some-parameter: some_value
```

Note the _aws_ and _gcp_ keys.

You'll notice that the output of `--help` will change depending on which parameters set you specify, e.g.

`tasks aws run --help`

`tasks gcp run --help`

Another thing to note is that the parameter set you specify is tracked during runtime as the variable _parameter_set_

You can use this behavior to detect when a given parameter set has been activated.

<a name="single-executable-releases"></a>
## Single-Executable Releases

This script also ships as a zipapp executable (similar to a windows .exe).

Head over to the [releases page](https://github.com/berttejeda/ansible-taskrunner/releases) for release downloads.

You can also build your own single-executable zipapp, as follows:

1. Make sure you have the [make-zipapp](https://github.com/berttejeda/make-zipapp) executable in your path
1. Invoking build tasks
  - Build zipapp: `./tasks.py -f build.yaml run -b`
  - Build zipapp and push to remote host (via scp): `./tasks.py -f build.yaml run -b -bp someserver.somedomain.local:/home/${USER-USERNAME}`

Read More on zipapps: [zipapp — Manage executable Python zip archives — Python 3.7.4rc2 documentation](https://docs.python.org/3/library/zipapp.html)
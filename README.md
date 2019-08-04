<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Overview](#overview)
- [TL;DR](#tldr)
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
  - [Populate the vars block - embedded make-style functions](#populate-the-vars-block---embedded-make-style-functions)
    - [About make-style functions](#about-make-style-functions)
      - [Bash example:](#bash-example)
      - [Python example:](#python-example)
      - [Ruby example:](#ruby-example)
  - [Add tasks](#add-tasks)
- [Usage Examples](#usage-examples)
- [Installation](#installation)
  - [More Examples](#more-examples)
- [Appendix](#appendix)
  - [Special Variables](#special-variables)
    - [ansible_playbook_command](#ansible_playbook_command)
    - [cli_provider](#cli_provider)
    - [__ansible_extra_options](#__ansible_extra_options)
    - [__tasks_file__](#__tasks_file__)
  - [Parameter Sets](#parameter-sets)
  - [Single-Executable Releases](#single-executable-releases)
- [License and Credits](#license-and-credits)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
<a name="top"></a>
<a name="overview"></a>
# Overview

This is a task runner that serves as a higher-level automation layer to ansible

The script expects an ansible-playbook file as the task manifest.

By default, this is a file named 'Taskfile.yaml' in the current working directory.

The inspiration for the tool comes from the gnu make command, which operates in similar fashion, i.e.

- A Makefile defines available build steps
- The make command consumes the Makefile at runtime and exposes these steps as command-line options

# TL;DR

- Ever wanted to add custom switches to the `ansible-playbook` command? Something like this:<br /> 
`ansible-playbook -i myinventory.txt -d dbhost1 -w webhost1 -t value1 myplaybook.yaml`
- Well, you can through the use of an ansible-playbook wrapper
- That's where `tasks` comes in:<br />
`tasks run -d dbhost1 -w webhost1 -t value1`<br />
translates to:<br />
`ansible-playbook -i /tmp/ansible-inventory16xdkrjd.tmp.ini -e dbhosts="dbhost1" -e webhosts="webhost1" -e some_value="value1" -e echo="True" Taskfile.yaml`

1. Jump down to the [usage examples](#usage-examples) to see this in action
2. Review the [installation](#installation) instructions if you want to test-drive it
3. Read on if you want to dig deeper into the tool

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
  - Makes it more difficult to package actions as roles
  - Duplicate efforts across codebase

<a name="proposed-solution"></a>
## Proposed Solution

Employ a pre-execution script that operates above the `ansible-playbook` command:
  - Accomplishes the same as the above, but in more uniform manner
  - Support for custom command-line parameters/flags
  - Embedded dynamic inventory
  - Embedded make-style shell functions

Advantages to this approach:
- Easier to manage
  - If you know YAML and Ansible, you can get started relatively quickly with writing ansible automation
- Single executable (/usr/local/bin/tasks)

Disadvantages:
- Target ansible controller needs to have the `tasks` command installed

[Back To Top](#top)
<a name="technical-details"></a>
# Technical Details

As stated in the [overview](#overview), this tool functions much like the *make* command in that it accepts an input file that essentially extends its cli options.

We create a specially formatted ansible-playbook that serves as a task definition file (by default, Taskfile.yaml).

This task definition file:

- Acts like a command-line script
- Is a valid ansible playbook (Taskfile.yaml), and can thus be launched with the `ansible-playbook` command
- Variables available to the pre-execution phase are also available to the ansible execution phase

In the following sections, we'll be building a sample manifest/playbook named *Taskfile.yaml*

[Back To Top](#top)
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

[Back To Top](#top)
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

[Back To Top](#top)
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

[Back To Top](#top)
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
      -d|--db-hosts: dbhosts ## Specify DB Host targets
      -w|--web-hosts: webhosts ## Specify Web Host targets
      -t|--some-parameter: some_value ## Specify some value
    optional_parameters:
      -l|--another-parameter: another_value ## Specify another value
      -A: hello ## Shortcut to the hello make-style function
      -PR: preflight_and_run ## Shortcut to the preflight_and_run make-style function
      --debug-mode: debug_mode ## Enable debug mode
```   

</details>

Notice the parameter definitions:
  - required_parameters
  - optional_paramters

These are yaml list objects that expose optional and required command-line options.

The syntax for the options is as follows:

```
Options                                      | Mapped Variable
-------------------------------------------- | ----------------------
-{{ short_option }}|--{{ long_option }}      | {{ mapped_variable }} ## {{ Help Text }}
-{{ switch }}                                | {{ mapped_variable }} (boolean) ## {{ Help Text }}
--{{ switch }}                               | {{ mapped_variable }} (boolean) ## {{ Help Text }}
```

Essentially, any option with a pipe '|' character in its name is evaluated as a click option, which means you must provide an argument to said option.

Anything else is treated as a switch, which evaluates to `True` if specified, and undefined otherwise (unless you provide a default in your `vars` declaration).

Also, an option's help text can be included alongside the mapped variable, and must conform to the following syntax: `## {{ HELP TEXT }}`

More Examples:

```
Options       | Mapped Variable
------------- | -------------
-f|--foo      | some_foo_variable ## This is some foo option
-b|--bar      | some_bar_variable ## This is some bar option
-F|--foo-bar  | some_other_variable ## This is some foo bar option
-a|--all-else | [remaining_args] (behaves like click's variadic arguments (nargs=*)) ## This option will 'eat' up all remaining commandline arguments
--some-option | some_switch (behaves like click switches, holds the value of True if specified) ## This is some boolean option
```

More flexibility can be achieved through the use of [parameter sets](#parameter-sets).

See the [appendix](#parameter_set) for more information.

[Back To Top](#top)
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
      -d|--db-hosts: dbhosts ## Specify DB Host targets
      -w|--web-hosts: webhosts ## Specify Web Host targets
      -t|--some-parameter: some_value ## Specify some value
    optional_parameters:
      -l|--another-parameter: another_value ## Specify another value
      -A: hello ## Shortcut to the hello make-style function
      -PR: preflight_and_run ## Shortcut to the preflight_and_run make-style function
      --debug-mode: debug_mode ## Enable debug mode
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

[Back To Top](#top)
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
      -d|--db-hosts: dbhosts ## Specify DB Host targets
      -w|--web-hosts: webhosts ## Specify Web Host targets
      -t|--some-parameter: some_value ## Specify some value
    optional_parameters:
      -l|--another-parameter: another_value ## Specify another value
      -A: hello ## Shortcut to the hello make-style function
      -PR: preflight_and_run ## Shortcut to the preflight_and_run make-style function
      --debug-mode: debug_mode ## Enable debug mode
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

<a name="populate-the-vars-block---embedded-make-style-functions"></a>
## Populate the vars block - embedded make-style functions

<details>
  <summary>Add embedded make-style functions: </summary>

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
      -d|--db-hosts: dbhosts ## Specify DB Host targets
      -w|--web-hosts: webhosts ## Specify Web Host targets
      -t|--some-parameter: some_value ## Specify some value
    optional_parameters:
      -l|--another-parameter: another_value ## Specify another value
      -A: hello ## Shortcut to the hello make-style function
      -PR: preflight_and_run ## Shortcut to the preflight_and_run make-style function
      --debug-mode: debug_mode ## Enable debug mode
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
        help: Say Hello
        hidden: false
        source: |-
          echo hello
      preflight_and_run:
        shell: bash
        help: Execute Preflight Tasks and Run
        hidden: false
        source: |-
          echo 'Running Preflight Tasks!'
          tasks run -d dbhost1 -w webhost1 -t value1
```

</details>

Notice the two switches `-A` and `-PR`.

These map to corresponding keys in the embedded `functions` stanza.
As such, specifying the options in your `tasks` invocation 
will short-circuit normal operation and execute the corresponding functions in the order you called them.

For usage examples, see the [appendix](#usage-examples).

<a name="about-make-style-functions"></a>
### About make-style functions

Let's briefly side-step into make-style functions 

The syntax for nesting these under the _functions_ key is as follows:

```
      name_of_function:
        shell: bash, ruby, or python
        help: Help Text to Display
        hidden: false/true
        source: |-
          {{ code }}
```

[Back To Top](#top)
<a name="bash-example"></a>
#### Bash example:

```
      hello:
        shell: bash
        help: Hello World in Bash
        hidden: false
        source: |-
          echo 'Hello World!'
```

<a name="python-example"></a>
#### Python example:

```
      hello:
        shell: python
        help: Hello World in Python
        hidden: false
        source: |-
          print('Hello World!')
```

<a name="ruby-example"></a>
#### Ruby example:

```
      hello:
        shell: ruby
        help: Hello World in Ruby
        hidden: false
        source: |-
          puts 'Hello World!'
```

[Back To Top](#top)
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
      -d|--db-hosts: dbhosts ## Specify DB Host targets
      -w|--web-hosts: webhosts ## Specify Web Host targets
      -t|--some-parameter: some_value ## Specify some value
    optional_parameters:
      -l|--another-parameter: another_value ## Specify another value
      -A: hello ## Shortcut to the hello make-style function
      -PR: preflight_and_run ## Shortcut to the preflight_and_run make-style function
      --debug-mode: debug_mode ## Enable debug mode
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
        help: Say Hello
        hidden: false
        source: |-
          echo hello
  tasks:
    - debug: 
        msg: |
          Hello from Ansible!
          You specified: {{ some_value }}
```

</details>

<a name="usage-examples"></a>
# Usage Examples

Quick usage examples:

* Display help for main command<br />
  `tasks --help`
* Display help for the *run* subcommand<br />
  `tasks run --help`
* Initialize your workspace<br />
  `tasks init`<br />
* Run the Tasksfile.yaml playbook, passing in additional options to the underlying subprocess<br />
  `tasks run -d dbhost1 -w webhost1 -t value1 ---raw '-vvv'`</br>
* Don't do anything, just echo the underlying shell command<br />
  `tasks run -d dbhost1 -w webhost1 -t value1 ---echo`<br />
  Result should be similar to:<br />
  `ansible-playbook -i C:\Users\${USERNAME}\AppData\Local\Temp\ansible-inventory16xdkrjd.tmp.ini -e dbhosts="dbhost1" -e webhosts="webhost1" -e some_value="value1" -e echo="True" Taskfile.yaml`
* Run the Tasksfile.yaml playbook<br />
  `tasks run -d dbhost1 -w webhost1 -t value1`
* Run the embedded function `preflight_and_run`<br />
  `tasks run -d dbhost1 -w webhost1 -t value1 -PR`
* Run the embedded functions `hello` and `preflight_and_run`<br />
  `tasks run -d dbhost1 -w webhost1 -t value1 -A -PR`

[Back To Top](#top)
<a name="installation"></a>
# Installation

Ansible-tasksrunner consists of the `tasks` binary (for now), and it can be installed in a few ways:

1. pip install ansible-taskrunner
2. pip install git+https://github.com/berttejeda/ansible-taskrunner.git
3. Obtaining a [release](#single-executable-releases)

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
Upon invoking the `tasks` command with the `---echo` flag, the underlying shell command would then be revealed as:

`python ${HOME}/ansible_2.7.8/ansible-playbook -i C:\Users\${USERNAME}\AppData\Local\Temp\ansible-inventory16xdkrjd.tmp.ini -e dbhosts="dbhost1" -e webhosts="webhost1" -e some_value="value1" -e echo="True" Taskfile.yaml`

[Back To Top](#top)
<a name="cli_provider"></a>
### cli_provider

You can override the underlying command-line provider in two ways:

- Via the tasks config file (see [examples](#examples))
- By defining the variable *cli_provider* in the specified Taskfile

As an example, suppose I define this variable in the above *Taskfile.yaml*, as follows:

```
- hosts: myhosts
  gather_facts: true
  become: true
  vars:
    cli_provider: bash
    # ...
```

Upon invoking the `tasks` command, you will note that the app no longer operates in an **ansible-playbook** mode, but rather as yaml-abstracted bash-script.

There are three cli-providers built in to the tasks command:

- ansible
- bash
- vagrant

<a name="__ansible_extra_options"></a>
### __ansible_extra_options

Apart from utilizing the `---raw` flag, you can specify additional options to pass to the underlying `ansible-playbook` subprocess by setting an appropriate value for the **__ansible_extra_options** Environmental variable.

<a name="__tasks_file__"></a>
### __tasks_file__

The **__tasks_file__** variable points to the current Taskfile.

It is available to the underlying subprocess shell.

[Back To Top](#top)
<a name="parameter_sets"></a>
## Parameter Sets

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
      -d|--db-hosts: dbhosts ## Specify DB Host targets
      -w|--web-hosts: webhosts ## Specify Web Host targets
      -t|--some-parameter: some_value ## Specify some value
```

Note the _aws_ and _gcp_ keys.

You'll notice that the output of `--help` will change depending on which parameter set you specify, e.g.

`tasks aws run --help`

`tasks gcp run --help`

Another thing to note is that the parameter set you specify is tracked during runtime as the variable _parameter_set_

You can use this behavior to detect when a given parameter set has been activated.

[Back To Top](#top)
<a name="single-executable-releases"></a>
## Single-Executable Releases

This script also ships as a zipapp executable (similar to a windows .exe).

Head over to the [releases page](https://github.com/berttejeda/ansible-taskrunner/releases) for release downloads.

You can also build your own single-executable zipapp, as follows:

1. Make sure you have the [make-zipapp](https://github.com/berttejeda/make-zipapp) executable in your path
1. Invoking build tasks
  - Build zipapp: `python ansible_taskrunner/cli.py -f Makefile.yaml run ---make zipapp`
  - Build zipapp and push to remote host (via scp): `python ansible_taskrunner/cli.py -f Makefile.yaml run ---make zipapp -bp someserver.somedomain.local:/home/${USER-USERNAME}`

Read More on zipapps: [zipapp — Manage executable Python zip archives — Python 3.7.4rc2 documentation](https://docs.python.org/3/library/zipapp.html)

[Back To Top](#top)
<a name="license-and-credits"></a>
# License and Credits

This project adopts the the MIT distribution License.

[Releases](https://github.com/berttejeda/ansible-taskrunner/releases) come bundled with the following opensource python packages:

- [click](https://github.com/pallets/click), licensed under BSD-3-Clause
- [pyYaml](https://github.com/yaml/pyyaml), licensed under MIT

Lastly, this package was created with Cookiecutter and the `audreyr/cookiecutter-pypackage` project template.

- Cookiecutter: https://github.com/audreyr/cookiecutter
- audreyr/cookiecutter-pypackage: https://github.com/audreyr/cookiecutter-pypackage

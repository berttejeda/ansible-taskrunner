<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Overview](#overview)
- [TL;DR](#tldr)
- [Use case and example](#use-case-and-example)
    - [Given](#given)
    - [The Challenge](#the-challenge)
    - [Investigation](#investigation)
    - [Assessment](#assessment)
    - [Proposed Solution](#proposed-solution)
- [Technical Details](#technical-details)
- [Creating a Task Manifest File](#creating-a-task-manifest-file)
    - [Add the hosts block](#add-the-hosts-block)
    - [Add the vars block](#add-the-vars-block)
    - [Populate the vars block - defaults](#populate-the-vars-block---defaults)
    - [Populate the vars block - cli options](#populate-the-vars-block---define-commands)
      - [Populate the vars block - cli options - mapped variables](#populate-the-vars-block---define-commands---mapped-variables)
    - [Populate the vars block - help/message](#populate-the-vars-block---helpmessage)
    - [Populate the vars block - embedded inventory](#populate-the-vars-block---embedded-inventory)
    - [Populate the vars block - external inventory](#populate-the-vars-block---external-inventory)
    - [Populate the vars block - embedded shell functions](#populate-the-vars-block---embedded-shell-functions)
        - [More about embedded shell functions](#more-about-embedded-shell-functions)
            - [Bash example:](#bash-example)
            - [Python example:](#python-example)
            - [Ruby example:](#ruby-example)
    - [Add tasks](#add-tasks)
- [Usage Examples](#usage-examples)
- [Installation](#installation)
    - [More Examples](#more-examples)
- [Appendix](#appendix)
    - [Bastion Mode](#bastion-mode)
    - [Special Variables](#special-variables)
        - [ansible_playbook_command](#ansible_playbook_command)
        - [cli_provider](#cli_provider)
        - [__ansible_extra_options](#__ansible_extra_options)
        - [__tasks_file__](#__tasks_file__)
        - [__parameter_sets__](#__parameter_sets__)
  - [Parameter Sets](#parameter-sets)
  - [Mutually Exclusive Options](#mutually-exclusive-options)
  - [Option Tags](#option-tags)
      - [Prompt option tag](#prompt-option-tag)
      - [Choice option tag](#choice-option-tag)
      - [Combining option tags](#combining-option-tags)
  - [Simple Templating](#simple-templating)
  - [Single-Executable Releases](#single-executable-releases)
  - [Unit Testing](#unit-testing)
- [TODO - Add more tests!](#todo---add-more-tests)
- [License and Credits](#license-and-credits)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
<a name="top"></a>
<a name="overview"></a>

# Overview

*ansible-taskrunner* is a cli app that is essentially an ansible wrapper.

It reads an ansible playbook file as its input, which serves as a _task manifest_.

If no task manifest is specified, the app will search for 'Taskfile.yaml' in the current working directory.

The inspiration for the tool comes from the gnu make command, which operates in similar fashion, i.e.

- A Makefile defines available build steps
- The make command consumes the Makefile at runtime and exposes these steps as command-line options

If you are running this tool from Windows, please read the section on [Bastion Mode](#bastion_mode)

# TL;DR

- Ever wanted to add custom switches to the `ansible-playbook` command? Something like this:<br /> 
`ansible-playbook -i myinventory.txt -d dbhost1 -w webhost1 -t value1 myplaybook.yaml`
- Well, you can through the use of an ansible-playbook wrapper
- That's where `tasks` comes in:<br />
`tasks run -a 1 -b bar -f foo -t local`<br />
translates to:<br />
`ansible-playbook -i /tmp/ansible-inventory16xdkrjd.tmp.ini -e foo="foo" -e bar="bar" -e playbook_taregets="local" -e all_else="1" Taskfile.yaml`

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
3. Ansible is the primary means of invoking business and operational processes across the numerous environments

<a name="the-challenge"></a>

## The Challenge

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

Employ a pre-execution script that operates at a layer above the `ansible-playbook` command:
- Accomplishes the same as the above, but in more uniform manner
- Support for custom command-line parameters/flags
- Embedded dynamic inventory
- Embedded shell shell functions

Advantages to this approach:
- Easier to manage
  - If you know YAML and Ansible, you can get started relatively quickly with writing ansible automation
- Single executable (/usr/local/bin/tasks)

Disadvantages:
- Target ansible controller needs to have the `tasks` command installed

[Back To Top](#top)
<a name="technical-details"></a>

# Technical Details

As stated in the [overview](#overview), this tool functions much like the *make* command in that 
it accepts an input file that essentially extends its cli options.

We create a specially formatted ansible-playbook that serves as a task manifest file (by default, Taskfile.yaml).

This task manifest file:

- Extends the `tasks` command
- Is a valid ansible playbook (Taskfile.yaml), and can thus be launched with the `ansible-playbook` command
- Variables available to the pre-execution phase are also available to the ansible execution phase

<a name="creating-a-task-manifest-file"></a>

# Creating a task manifest file

In the following sections, we'll be building a sample manifest/playbook.

Start by opening up your favorite text/IDE/editor and creating 
a new task manifest YAML file named *Taskfile.yaml*.

<a name="add-the-hosts-block"></a>

## Add the hosts block

Add hosts, gather_facts, etc:

<details>
  <summary>Click to Expand</summary>

*Taskfile.yaml*

```
### The hosts block
- hosts: myhosts
  gather_facts: true
  become: true
```

</details>

<a name="add-the-vars-block"></a>

## Add the vars block

Remember, the task runner will ultimately be calling the `ansible-playbook` command against 
this very same file, <br />so it must be a valid ansible playbook.

Let's add the 'vars' block, which allows us to populate some default values:

<details>
  <summary>Click to Expand</summary>

*Taskfile.yaml*

```
### The hosts block
- hosts: myhosts
  gather_facts: true
  become: true
### The vars block
  vars:
```

</details>

<a name="populate-the-vars-block---defaults"></a>

## Populate the vars block - defaults

Let's add some default variables to the playbook:

<details>
  <summary>Click to Expand</summary>

*Taskfile.yaml*

```
### The hosts block
- hosts: myhosts
  gather_facts: true
  become: true
  ### The vars block  
  vars:
    var1: value1
    var2: value2
    var3: value3
    var4: |-
      This is a multi-line value
      of type string
    var5:
      - listvalue1
      - listvalue2
      - listvalue3
      - listvalue4
    var6:
      some_key:
        some_child_key: dictvalue1
    var7: $(echo some_value)
    dbhosts:
      - dbhost1
      - dbhost2
      - dbhost3
    webhosts:
      - webhost1
      - webhost2
      - webhost3
```
</details>

<br />As you can see, we've defined a number of variables holding different values.

The rules for evaluation of these are as follows:<br /><br />


```
Variable                                     | Ansible Evaluation      | Shell Function Evaluation
-------------------------------------------- | ----------------------- | -----------------------
str_var: value1                              | String                  | String
num_var: 3                                   | Digit                   | String
multiline_var: |                             | Multiline String        | String (heredoc)
  This is a multi-line value                 |                         |
  of type string                             |                         |
list_var:                                    | List Object             | String (heredoc)
  - item1                                    |                         |
  - item2                                    |                         |
dict_var:                                    | Dictionary Object       | JSON String (heredoc)
  key1: somevalue1                           |                         |
  key2: somevalue2                           |                         |
shell_var: $(grep somestring /some/file.txt) | Depends on output       | String
```

[Back To Top](#top)

<a name="populate-the-vars-block---define-commands"></a>
## Populate the vars block - define commands

Next, we define the available commands:

<details>
  <summary>Click to Expand</summary>

*Taskfile.yaml*

```
### The hosts block
- hosts: myhosts
  gather_facts: true
  become: true
  ### The vars block  
  vars:
    var1: value1
    var2: value2
    var3: value3
    var4: |-
      This is a multi-line value
      of type string
    var5:
      - listvalue1
      - listvalue2
      - listvalue3
      - listvalue4
    var6:
      some_key:
        some_child_key: dictvalue1
    var7: $(echo some_value)
    dbhosts:
      - dbhost1
      - dbhost2
      - dbhost3
    webhosts:
      - webhost1
      - webhost2
      - webhost3
    ### The commands block
    commands:
      run:
        options:
          required:
            -f|--foo: some_foo_variable ## This is some foo option
            -b|--bar: some_bar_variable ## This is some bar option
            -t|--targets: playbook_targets ## Playbook targets
            -a|--all-else: [remaining_args] ## (behaves like [click](https://github.com/pallets/click)'s variadic arguments (nargs=\*)), this option will 'eat' up all remaining commandline arguments
            --some-switch: some_switch ## (behaves like [click](https://github.com/pallets/click) switches, holds the value of True if specified), this is some boolean option
          optional:
            -A: hello ## Invoke the 'hello' shell function
            -B: goodbye ## Invoke the 'goodbye' shell function
            --debug-mode: debug_mode ## Enable debug logging
```   
</details>

<br />
Notice the parameter definitions for the `run` subcommand:

- options.required
- options.optional

These are yaml list objects that expose optional and required command-line options for the given subcommand.

The syntax for defining options is as follows:

```
-{{ short_option }}|--{{ long_option }}: {{ mapped_variable }} ## {{ Help Text }}
-{{ switch }}: {{ mapped_variable }} ## {{ Help Text }}
--{{ switch }}: {{ mapped_variable }} ## {{ Help Text }}
```

Essentially, any option with a pipe '|' character in its name is evaluated as a standard [click](https://github.com/pallets/click) option, which means you must provide it an argument.

Anything else is treated as a switch, which evaluates to `True` if specified, and undefined otherwise (unless you provide a default in your `vars` declaration).

An option's help text can be included alongside the mapped variable, and must conform to the following syntax: <br />
`## {{ HELP TEXT }}`

So from the example above, we have:

```
| Option              | Mapped Variable                                    |   Help Text String                            |
|:--------------------|:---------------------------------------------------|:----------------------------------------------|
| -f|--foo            | some_foo_variable                                  | ## This is some foo option                    |
| -b|--bar            | some_bar_variable                                  | ## This is some bar option                    |
| -t|--targets        | playbook_targets                                   | ## ## Playbook targets                        |
| --some-switch       | some_switch                                        | Behaves like click switches, holds the        |
                                                                           | value of 'True' if specified)                 |
| -A                  | hello                                              | Invoke the 'hello' embedded shell function    |
| -B                  | goodbye                                            | Invoke the 'goodbye' embedded shell function  |
| --debug-mode        | debug_mode                                         | Sets debug_mode to true                       |
```

**Important Note**: In the above example, the `-A` option points to a special mapped variable that itself maps to a shell 
function defined in the subcommand's functions directive. We'll discuss this more in [section]().

<a name="populate-the-vars-block---cli-options---mapped-variables"></a>

### Populate the vars block - cli options - mapped variables

As I mentioned before, the above mapped variables can be used **during runtime**, 
that is, they can be referenced in any defined shell functions, 
embedded inventory logic, as well as during ansible execution.

Consider the `-f|-foo` from the example.

Whatever argument you pass to this option becomes the value for the mapped variable `some_foo_variable`.

Again, this variable is made available to the underlying subprocess call, and thus to ansible.

So when we call the tasks command like so `tasks run -f foo` the value for the `some_foo_variable` becomes `foo`.

<a name="populate-the-vars-block---helpmessage"></a>

## Populate the vars block - help/message

Next, we add the help/message section:

<details>
  <summary>Click to Expand</summary>

*Taskfile.yaml*

```
### The hosts block
- hosts: myhosts
  gather_facts: true
  become: true
  ### The vars block  
  vars:
    var1: value1
    var2: value2
    var3: value3
    var4: |-
      This is a multi-line value
      of type string
    var5:
      - listvalue1
      - listvalue2
      - listvalue3
      - listvalue4
    var6:
      some_key:
        some_child_key: dictvalue1
    var7: $(echo some_value)
    dbhosts:
      - dbhost1
      - dbhost2
      - dbhost3
    webhosts:
      - webhost1
      - webhost2
      - webhost3
    ### The commands block
    commands:
      run:
        options:
          required:
            -f|--foo: some_foo_variable ## This is some foo option
            -b|--bar: some_bar_variable ## This is some bar option
            -t|--targets: playbook_targets ## Playbook targets
            -a|--all-else: [remaining_args] ## (behaves like [click](https://github.com/pallets/click)'s variadic arguments (nargs=\*)), this option will 'eat' up all remaining commandline arguments
            --some-switch: some_switch ## (behaves like [click](https://github.com/pallets/click) switches, holds the value of True if specified), this is some boolean option
          optional:
            -A: hello ## Invoke the 'hello' shell function
            -B: goodbye ## Invoke the 'goodbye' shell function
            --debug-mode: debug_mode ## Enable debug logging
        ### The help message
        help:
          message: |
            Invoke the 'run' command 
          epilog: |
            This line will be displayed at the end of the help text message
          examples:
            - example1: |
                tasks $command
            - example2: |
                Usage example 2
```

</details>

Running `tasks run --help` should return the list of parameters along with the help message you defined.

<a name="populate-the-vars-block---embedded-shell-functions"></a>

## Populate the vars block - embedded shell functions

<details>
  <summary>Add embedded shell functions: </summary>

*Taskfile.yaml*

```
### The hosts block
- hosts: myhosts
  gather_facts: true
  become: true
  ### The vars block  
  vars:
    var1: value1
    var2: value2
    var3: value3
    var4: |-
      This is a multi-line value
      of type string
    var5:
      - listvalue1
      - listvalue2
      - listvalue3
      - listvalue4
    var6:
      some_key:
        some_child_key: dictvalue1
    var7: $(echo some_value)
    dbhosts:
      - dbhost1
      - dbhost2
      - dbhost3
    webhosts:
      - webhost1
      - webhost2
      - webhost3
    ### The commands block
    commands:
      run:
        options:
          required:
            -f|--foo: some_foo_variable ## This is some foo option
            -b|--bar: some_bar_variable ## This is some bar option
            -t|--targets: playbook_targets ## Playbook targets
            -a|--all-else: [remaining_args] ## (behaves like [click](https://github.com/pallets/click)'s variadic arguments (nargs=\*)), this option will 'eat' up all remaining commandline arguments
            --some-switch: some_switch ## (behaves like [click](https://github.com/pallets/click) switches, holds the value of True if specified), this is some boolean option
          optional:
            -A: hello ## Invoke the 'hello' shell function
            -B: goodbye ## Invoke the 'goodbye' shell function
            --debug-mode: debug_mode ## Enable debug logging
        ### The help message
        help:
          message: |
            Invoke the 'run' command 
          epilog: |
            This line will be displayed at the end of the help text message
          examples:
            - example1: |
                tasks $command
            - example2: |
                Usage example 2
        ### Embedded shell functions
        functions:
          hello:
            shell: bash
            help: Say hello
            source: |-
              echo Hello! The value for var1 is $var1
          goodbye:
            shell: bash
            help: Say goodbye
            source: |-
              echo The value for var1 is $var1. Goodbye!
```

</details>

Notice the two switches `-A` and `-B`, with mapped variables _hello_ and _goodbye_, respecitively.

These mapped variables correspond to keys in the `functions` block.

As such, specifying either or both `-A` and `-B` in your `tasks` invocation<br />
will short-circuit normal operation and execute the corresponding functions<br /> 
in the order in which you call them.

Try it yourself by running:

- `tasks run -a 1 -b bar -f foo -t local -A -B`
- `tasks run -a 1 -b bar -f foo -t local -B -A`

For more usage examples, see the [appendix](#usage-examples).

<a name="more-about-embedded-shell-functions"></a>

### More about embedded shell functions

Let's briefly side-step into embedded shell functions.

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
<a name="populate-the-vars-block---embedded-inventory-expression"></a>

## Populate the vars block - embedded inventory expression

A useful feature of this tool is the ability to define your ansible inventory as an embedded expression in the Taskfile itself.

When the inventory is defined in this manner, the logic is as follows:

- The embedded inventory expression is evaluated
- An ephemeral inventory file is created with the<br />
  contents of this file being the output, or result, of that expression
- The fully qualified path to the ephemeral inventory file is specified as the<br />
  argument to the `ansible-playbook` inventory parameter `-i`

Let's define our embedded inventory expression:

<details>
  <summary>Click to Expand</summary>

*Taskfile.yaml*

```
### The hosts block
- hosts: myhosts
  gather_facts: true
  become: true
  ### The vars block  
  vars:
    var1: value1
    var2: value2
    var3: value3
    var4: |-
      This is a multi-line value
      of type string
    var5:
      - listvalue1
      - listvalue2
      - listvalue3
      - listvalue4
    var6:
      some_key:
        some_child_key: dictvalue1
    var7: $(echo some_value)
    dbhosts:
      - dbhost1
      - dbhost2
      - dbhost3
    webhosts:
      - webhost1
      - webhost2
      - webhost3
    ### The commands block
    commands:
      run:
        options:
          required:
            -f|--foo: some_foo_variable ## This is some foo option
            -b|--bar: some_bar_variable ## This is some bar option
            -t|--targets: playbook_targets ## Playbook targets
            -a|--all-else: [remaining_args] ## (behaves like [click](https://github.com/pallets/click)'s variadic arguments (nargs=\*)), this option will 'eat' up all remaining commandline arguments
            --some-switch: some_switch ## (behaves like [click](https://github.com/pallets/click) switches, holds the value of True if specified), this is some boolean option
          optional:
            -A: hello ## Invoke the 'hello' shell function
            -B: goodbye ## Invoke the 'goodbye' shell function
            --debug-mode: debug_mode ## Enable debug logging
        ### The help message
        help:
          message: |
            Invoke the 'run' command 
          epilog: |
            This line will be displayed at the end of the help text message
          examples:
            - example1: |
                tasks $command
            - example2: |
                Usage example 2
        ### Embedded shell functions
        functions:
          hello:
            shell: bash
            help: Say hello
            source: |-
              echo Hello! The value for var1 is $var1
          goodbye:
            shell: bash
            help: Say goodbye
            source: |-
              echo The value for var1 is $var1. Goodbye!
    ### The embedded inventory expression              
    inventory: |
      [local]
      localhost ansible_connection=local      
      [web-hosts]
      $(echo -e "${webhosts}" | tr ',' '\n')
      [db-hosts]
      $(echo -e "${dbhosts}" | tr ',' '\n')
      [myhosts:children]
      web-hosts
      db-hosts
```

</details>

As you can see, the embedded inventory definition is somewhat dynamic in that<br />
it gets evaluated based on the output of inline shell commands.

Let's focus on the variable _$webhosts_.

As per the logic described [above](#populate-the-vars-block---defaults), the variable $webhosts is a heredoc with a value of:

```
webhosts=$(cat <<EOF
webhost1
webhost2
webhost3
EOF
)
```

As such, the _web-hosts_ group in the embedded inventory expression ...
```
      [web-hosts]
      $(echo -e "${webhosts}" | tr ',' '\n')
```

... will evaluate to:

```
[web-hosts]
webhost1
webhost2
webhost3
```

Also, notice how the inline shell command tranforms commas into newline characters by way of the transform (`tr`) command.

This makes it so that if we were to have defined the _webhosts_ variable<br />
in the Tasksfile as `webhosts: webhost1,webhost2,webhost3`, it would have had the same outcome<br />
as defining it as a list object in the _vars_ block.

<a name="populate-the-vars-block---external-inventory"></a>

## Populate the vars block - external inventory

Let's specify an external inventory file instead of an embedded inventory definition:

<details>
  <summary>Click to Expand</summary>

*Taskfile.yaml*

```
### The hosts block
- hosts: myhosts
  gather_facts: true
  become: true
  ### The vars block  
  vars:
    var1: value1
    var2: value2
    var3: value3
    var4: |-
      This is a multi-line value
      of type string
    var5:
      - listvalue1
      - listvalue2
      - listvalue3
      - listvalue4
    var6:
      some_key:
        some_child_key: dictvalue1
    var7: $(echo some_value)
    dbhosts:
      - dbhost1
      - dbhost2
      - dbhost3
    webhosts:
      - webhost1
      - webhost2
      - webhost3
    ### The commands block
    commands:
      run:
        options:
          required:
            -f|--foo: some_foo_variable ## This is some foo option
            -b|--bar: some_bar_variable ## This is some bar option
            -t|--targets: playbook_targets ## Playbook targets
            -a|--all-else: [remaining_args] ## (behaves like [click](https://github.com/pallets/click)'s variadic arguments (nargs=\*)), this option will 'eat' up all remaining commandline arguments
            --some-switch: some_switch ## (behaves like [click](https://github.com/pallets/click) switches, holds the value of True if specified), this is some boolean option
          optional:
            -A: hello ## Invoke the 'hello' shell function
            -B: goodbye ## Invoke the 'goodbye' shell function
            --debug-mode: debug_mode ## Enable debug logging
        ### The help message
        help:
          message: |
            Invoke the 'run' command 
          epilog: |
            This line will be displayed at the end of the help text message
          examples:
            - example1: |
                tasks $command
            - example2: |
                Usage example 2
        ### Embedded shell functions
        functions:
          hello:
            shell: bash
            help: Say hello
            source: |-
              echo Hello! The value for var1 is $var1
          goodbye:
            shell: bash
            help: Say goodbye
            source: |-
              echo The value for var1 is $var1. Goodbye!
    ### External inventory file               
    inventory: '/some/path/some/inventory.yaml'
```

</details>

Specifying the path to a file as the inventory overrides the use of the ephemeral<br />
inventory file that is used when the inventory definition is an embedded expression.

[Back To Top](#top)
<a name="add-tasks"></a>

## Add tasks

Finally, let's add some proper ansible tasks!

<details>
  <summary>Click to Expand</summary>

*Taskfile.yaml*

```
### The hosts block
- hosts: myhosts
  gather_facts: true
  become: true
  ### The vars block  
  vars:
    var1: value1
    var2: value2
    var3: value3
    var4: |-
      This is a multi-line value
      of type string
    var5:
      - listvalue1
      - listvalue2
      - listvalue3
      - listvalue4
    var6:
      some_key:
        some_child_key: dictvalue1
    var7: $(echo some_value)
    dbhosts:
      - dbhost1
      - dbhost2
      - dbhost3
    webhosts:
      - webhost1
      - webhost2
      - webhost3
    ### The commands block
    commands:
      run:
        options:
          required:
            -f|--foo: some_foo_variable ## This is some foo option
            -b|--bar: some_bar_variable ## This is some bar option
            -t|--targets: playbook_targets ## Playbook targets
            -a|--all-else: [remaining_args] ## (behaves like [click](https://github.com/pallets/click)'s variadic arguments (nargs=\*)), this option will 'eat' up all remaining commandline arguments
            --some-switch: some_switch ## (behaves like [click](https://github.com/pallets/click) switches, holds the value of True if specified), this is some boolean option
          optional:
            -A: hello ## Invoke the 'hello' shell function
            -B: goodbye ## Invoke the 'goodbye' shell function
            --debug-mode: debug_mode ## Enable debug logging
        ### The help message
        help:
          message: |
            Invoke the 'run' command 
          epilog: |
            This line will be displayed at the end of the help text message
          examples:
            - example1: |
                tasks $command
            - example2: |
                Usage example 2
        ### Embedded shell functions
        functions:
          hello:
            shell: bash
            help: Say hello
            source: |-
              echo Hello! The value for var1 is $var1
          goodbye:
            shell: bash
            help: Say goodbye
            source: |-
              echo The value for var1 is $var1. Goodbye!
    ### The embedded inventory expression              
    inventory: |
      [local]
      localhost ansible_connection=local
      [web-hosts]
      $(echo -e "${webhosts}" | tr ',' '\n')
      [db-hosts]
      $(echo -e "${dbhosts}" | tr ',' '\n')
      [myhosts:children]
      web-hosts
      db-hosts            
  tasks:
    - debug: 
        msg: |
          Hello from Ansible!
          You specified the following variables: 
          - foo: {{ some_foo_variable }}
          - bar: {{ some_bar_variable }}
          - all_else: {{ remaining_args }}
          - some_switch: {{ some_switch }}
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
* Run the Taskfile.yaml playbook, passing in additional options to the underlying subprocess<br />
  `tasks run -a 1 -b bar -f foo -t local ---raw -vvv`</br>
* Don't do anything, just echo the underlying shell command<br />
  `tasks run -a 1 -b bar -f foo -t local ---echo`<br />
  Result should be similar to:<br />
  `ansible-playbook -i /var/folders/5f/4g4xnnv958q52108qxd2rj_r0000gn/T/ansible-inventorytlmz2hpz.tmp.ini -e var1="${var1}" ... Taskfile.yaml`
* Run the Taskfile.yaml playbook<br />
  `tasks run -a 1 -b bar -f foo -t local`
* Run the embedded function `hello`<br />
  `tasks run -a 1 -b bar -f foo -t local -A`
* Run the embedded functions `hello` and `goodbye`<br />
  `tasks run -a 1 -b bar -f foo -t local -A -B`

[Back To Top](#top)
<a name="installation"></a>

# Installation

Ansible-taskrunner consists of the `tasks` binary (for now), and it can be installed in a few ways:

1. pip install ansible-taskrunner
2. pip install git+https://github.com/berttejeda/ansible-taskrunner.git
3. Obtaining a [release](#single-executable-releases)

Note: You'll need to pre-install a python distribution for the Windows MSI release.
Not yet sure if I am doing something wrong or if that's by design.
I lean toward the former :|

<a name="more-examples"></a>

## More Examples

Review the [examples](examples) directory for more hands-on usage samples.

<a name="appendix"></a>

# Appendix

<a name="bastion_mode"></a>

## Bastion Mode

If you're launching the `tasks` command from a Windows host, this tool will automatically execute in _Bastion Mode_

Under Bastion Mode, the `tasks` command will:
- Execute the `ansible-playbook` subprocess via a _bastion host_, i.e. a remote machine that _should have_ `ansible` installed
- This is done via ssh using the [paramiko](http://www.paramiko.org/) module

Running in Bastion Mode requires a configuration file containing the ssh connection settings.

To initialize this configuration file, you can simply run `tasks init`.

For full usage options, enter in `tasks init --help`.

Once you've initialized the configuration file, you should see *sftp-config.json* in your workspace.

This configuration file is fashioned after the [sftp](https://packagecontrol.io/packages/SFTP)<br />
plugin for [Sublime Text](https://www.sublimetext.com/) and is thus compatible.

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
    var1: value1
    var2: value2
    var3: value3
    # ...
```
Upon invoking the `tasks` command with the `---echo` flag:

- The temporary inventory is revealed as:<br />

```
if [[ ($inventory) && ( "True" == "True") ]];then
echo -e """$(cat <<EOF
[local]
localhost ansible_connection=local
[web-hosts]
$(echo -e "${webhosts}" | tr ',' '\n')
[db-hosts]
$(echo -e "${dbhosts}" | tr ',' '\n')
[myhosts:children]
web-hosts
db-hosts            
EOF
)"""| while read line;do
 eval "echo -e ${line}" >> "/var/folders/5f/4g4xnnv958q52108qxd2rj_r0000gn/T/ansible-inventorytlmz2hpz.tmp.ini";
done
fi;
```

- And the underlying shell command would be revealed as:<br />

`python ${HOME}/ansible_2.7.8/ansible-playbook -i /var/folders/5f/4g4xnnv958q52108qxd2rj_r0000gn/T/ansible-inventorytlmz2hpz.tmp.ini -e dbhosts="dbhost1" -e webhosts="webhost1" -e some_value="value1" -e echo="True" Taskfile.yaml`

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

### __ansible_extra_options__

Apart from utilizing the `---raw` flag, you can specify additional options to pass to the underlying `ansible-playbook` subprocess by setting an appropriate value for the **\_\_ansible_extra_options\_\_** Environmental variable.

<a name="__tasks_file__"></a>

### __tasks_file__

The **\_\_tasks_file\_\_** variable points to the current Taskfile.

It is available to the underlying subprocess shell.

### __command__

The **\_\_command\_\_** variable points to the name of the invoked subcommand.

It is available to the underlying subprocess shell.

[Back To Top](#top)
<a name="mutually-exclusive-options"></a>

## Mutually Exclusive Options

Taken from [Mutually exclusive option groups in python Click - Stack Overflow](https://stackoverflow.com/questions/37310718/mutually-exclusive-option-groups-in-python-click).

Suppose you want a set of options such that:
- You want to accept one option but only if another, related option has not been specified

You can accomplish this by defining your options with an ' or ' format, as with:

```
-a|--auth-token: auth_token ## Specify auth token
-u|--username or -a|--auth-token: username ## Specify Username
-p|--password or -a|--auth-token: password ## Specify Password
```

In the above configuration, calling the options for 
username and password will render the option for auth token _optional_, 
that is, you don't need to specify the auth token if you've specified 
the username and password.

A sample is provided in the [examples](examples) directory.

<a name="option-tags"></a>
## Option Tags

Option tags provide an elegant mechanism for further 
customizing the behavior of your command-line options.

The logic treats anything after the first two pipe ('|') characters as option tags.

So far, four option tags are honored, and these are:
- prompt
- sprompt
- choice
- env

Note that these can be combined.

<a name="prompt-options"></a>
### Prompt option tag

Taken from [Options — Click Documentation (7.x)](https://click.palletsprojects.com/en/7.x/options/#prompting)

Suppose you want a set of *optional* options such that:
- You will be prompted if said option is not provided a value

You can accomplish this by defining your options with a 'prompt' option tag, as with:
```
optional_parameters:
  -u|--username|prompt: username ## Specify password
  -p|--password|sprompt: password ## Specify password
```

In the above configuration, *not* calling the options for 
username and password invoke a prompt

There are two types of option tags related to prompting:
- prompt
- sprompt

The latter will hide the input, and so is best used for accepting sensitive input, such as passwords.

A sample is provided in the [examples](examples) directory.

<a name="choice-options"></a>
### Choice option tag

Taken from [Options — Click Documentation (7.x)](https://click.palletsprojects.com/en/7.x/options/#choice-options)

Suppose you want a set of options such that:
- The value you provide for such an option must come from a list of pre-defined values.

You can accomplish this by defining your options with a 'choice' option tag, as with:

```
-s|--selection|choice: selection ## Specify a selection
  - choice1
  - choice2
  - choice3
```

In the above configuration, providing a value for _selection_
will limit you to the values defined in the option list.

A sample is provided in the [examples](examples) directory.


<a name="combining-option-tags"></a>
### Combining option tags

Suppose you want a set of options that combine some or all of the behavior described above.

You can accomplish this by defining your options with a multiple tags, as with:

```
-u|--username|env|prompt: username ## Specify password
-p|--password|env|sprompt: password ## Specify password
```

Note that the _choice_ option tag only works with values that are a list type, 
so you can't do something like:

```
-u|--username|env|choice: username ## Specify password
-p|--password|env|choice: password ## Specify password
```

<a name="simple-templating"></a>

## Simple Templating

As of version 1.1.5, simple templating is available to the following objects:

- Help messages
- Examples
- Options
- Options values

What this means is that we expose a limited set of internal variables to the above.

As an example:

```
      examples:
        - example1: |
            tasks -f $tf_path --foo foo --bar bar
        - example2: |
            tasks -f $tf_path --foo foo --baz baz
```            

In the above strings, `$tf_path` will expand to the internal variable tf_path,
which holds the relative path to the current tasks file.

Below is a list of available variables for your convenience:

- cli_args
- cli_args_short
- parameter_sets
- tf_path

```
Variable        | Description
-------------   | -------------
exe_path        | The absolute path to the tasks executable
cli_args        | The current command-line invocation
cli_args_short  | The current command-line invocation, minus the executable
parameter_sets  | The parameter sets you have invoked
sys_platform    | The OS Platform as detected by Python
tf_path         | The relative path to the specified Taskfile
```

[Back To Top](#top)
<a name="single-executable-releases"></a>

## Single-Executable Releases

This script also ships as a zipapp executable (similar to a windows .exe).

Head over to the [releases page](https://github.com/berttejeda/ansible-taskrunner/releases) for release downloads.

You can also build your own single-executable zipapp, as follows:

1. Make sure you have the [make-zipapp](https://github.com/berttejeda/make-zipapp) executable in your path
1. Invoking build tasks
  - Build zipapp: `python ansible_taskrunner/cli.py -f Makefile.yaml run ---make zipapp`

Read More on zipapps: [zipapp — Manage executable Python zip archives — Python 3.7.4rc2 documentation](https://docs.python.org/3/library/zipapp.html)

<a name="unit-testing"></a>

## Unit Testing

To run all tests, simply call the test script, as with:

`python tests/test_ansible_taskrunner.py`

# TODO - Add more tests!

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

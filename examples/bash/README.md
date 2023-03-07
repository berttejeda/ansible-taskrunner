<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Bash Example](#bash-example)
- [Exercises](#exercises)
  - [Install and Obtain Project Files](#install-and-obtain-project-files)
  - [Ping Google Function](#ping-google-function)
- [Learning Points](#learning-points)
- [Caveats](#caveats)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<a name="bash-example"></a>
# Bash Example

The Taskfile here consists of an ansible playbook that has been repurposed as a bastardized bash script.

Essentially, it's a stripped down ansible playbook that holds bash functions represented in YAML syntax.

<a name="exercises"></a>
# Exercises

<a name="install-and-obtain-project-files"></a>
## Install and Obtain Project Files

* `pip install ansible-taskrunner` OR<br />
* `pip install git+https://github.com/berttejeda/ansible-taskrunner.git` OR<br />
* Download the latest [release](https://github.com/berttejeda/ansible-taskrunner/releases)<br />
* Clone the git repository and navigate to the example<br />

```
git clone https://github.com/berttejeda/ansible-taskrunner.git
cd ansible-taskrunner/exercises/bash
```

<a name="display-usage"></a>
## Display Usage

`tasks run --help`

```
This is essentially a stripped down ansible playbook that holds bash functions
represented in YAML syntax
The neat part about this is that you get to easily adjust cli options for your
YAML-organized Bash script :)

Options:
  --version                Show the version and exit.
  ---make, ---m TEXT       Call shell function
  ---raw TEXT              Specify raw options for underlying subprocess
  ---echo                  Don't run, simply echo underlying commands
  --ping-google            Invoke the 'ping_google' shell function
  -h, --target-hosts TEXT  Specify target hosts to ping
  --help                   Show this message and exit.


None
Examples:
- You want to ping google's dns servers:
tasks run -h 8.8.8.8
- You want to run the ping_google embedded function:
tasks run --ping-google

Available shell functions:
ping_google: Ping Google's DNS Server
```

<a name="ping-google-function"></a>
## Ping Google Function

* Let's run the `ping_google` embedded function<br />
```
tasks run --ping-google
```

<a name="learning-points"></a>
# Learning Points

- You are able to easily adjust cli options for your YAML-organized Bash script :)
- You can get pretty creative with how you proceed with this approach

<a name="caveats"></a>
# Caveats

- As with any piece of automation, you can do some serious damage given the right set of commands and functions.
- Please, for the love of FSM, make sure you know what you're doing 😎
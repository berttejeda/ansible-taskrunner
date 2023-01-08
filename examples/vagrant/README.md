<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Vagrant Command Example](#vagrant-command-example)
- [Exercises](#exercises)
  - [Install and Obtain Project Files](#install-and-obtain-project-files)
  - [Display Usage](#display-usage)
  - [Bring up an Ubuntu Xenial 64 Box](#bring-up-an-ubuntu-xenial-64-box)
  - [Bring up an Oracle Enterprise Linux 64 Box](#bring-up-an-oracle-enterprise-linux-64-box)
- [Learning Points](#learning-points)
- [Caveats](#caveats)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<a name="vagrant-command-example"></a>
# Vagrant Command Example

The Taskfile here consists of an ansible playbook that has been repurposed as a bastardized bash script.

We've also made it into a meta-automation step to the `vagrant` command.

Essentially, this is a:
- Stripped down ansible playbook that holds bash functions represented in YAML syntax
- Embedded functions are meant to facilitate interaction with the vagrant command, e.g. providing some custom cli options and the like

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
Essentially, this is a:
- Stripped down ansible playbook that holds bash functions represented in YAML
syntax
- Embedded functions are meant to facilitate interaction with the vagrant
command, e.g. providing some custom cli options and the like

Options:
  --version             Show the version and exit.
  ---make, ---m TEXT    Call shell function
  ---raw TEXT           Specify raw options for underlying subprocess
  ---echo               Don't run, simply echo underlying commands
  --oel76               Invoke the 'vagrant_up_oel76' shell function
  --xenial              Invoke the 'vagrant_up_xenial' shell function
  ---vagrant-test-flag  Set the _vagrant_test_flag value to true
  --help                Show this message and exit.


None
Examples:
- You want to fire up an Ubuntu Xenial x64 machine:
tasks run --xenial
- You want to fire up an Oracle Enterprise Linux 7.6 x64 machine:
tasks run --oel76

Available shell functions:
vagrant_up_oel76: Bring up an Oracle Enterprise Linux 7.6 x64 Virtual Machine
vagrant_up_xenial: Bring up an Ubuntu Xenial x64 Virtual Machine
```

<a name="bring-up-an-ubuntu-xenial-64-box"></a>
## Bring up an Ubuntu Xenial 64 Box

* Let's fire up an Ubuntu Xenial 64 Virtual Machine<br />
```
tasks run --xenial
```

<a name="bring-up-an-oracle-enterprise-linux-64-box"></a>
## Bring up an Oracle Enterprise Linux 64 Box

* Let's fire up an  Oracle Enterprise Linux 64 Virtual Machine<br />
```
tasks run --oel76
```

<a name="learning-points"></a>
# Learning Points

- You are able to easily adjust cli options for your YAML-organized Bash script :)
- You are able to seamlessly interact with the vagrant command
- You can get pretty creative with how you proceed with this approach
- This is how I'm managing my vagrant environments at the moment
	- See: ## TODO: Share your vagrant setup

<a name="caveats"></a>
# Caveats

- Consider this **experimental**, as I have not had extensive experience vetting the possible *gotchas* with this configuration (i.e. calling the `vagrant` command via python **subprocess**)
- As with any piece of automation, you can do some serious damage given the right set of commands and functions.
- Please, for the love of FSM, make sure you know what you're doing 😎
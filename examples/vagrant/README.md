<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Vagrant Command Example](#vagrant-command-example)
- [Exercises](#exercises)
  - [Obtain Project Files](#obtain-project-files)
  - [Bring up Ubuntu Xenial 64 Box](#bring-up-ubuntu-xenial-64-box)
  - [Bring up an Oracle Enterprise Linux 64 Box](#bring-up-an-oracle-enterprise-linux-64-box)
- [Learning Points](#learning-points)
- [Caveats](#caveats)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<a name="vagrant-command-example"></a>
# Vagrant Command Example

The Tasksfile here consists of an ansible playbook that has been repurposed as a bastardized bash script.

We've also made it into a meta-automation step to the `vagrant` command.

Essentially, this is a:
- Stripped down ansible playbook that holds bash functions represented in YAML syntax
- Embedded functions are meant to facilitate interaction with the vagrant command, e.g. providing some custom cli options and the like

<a name="exercises"></a>
# Exercises

<a name="obtain-project-files"></a>
## Obtain Project Files

* Download the latest [release](https://github.com/berttejeda/ansible-taskrunner/releases)<br />
* Clone the git repository and navigate to the example<br />

```
git clone https://github.com/berttejeda/ansible-taskrunner.git
cd ansible-taskrunner/exercises/bash
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
	- See: 

<a name="caveats"></a>
# Caveats

- Consider this **experimental**, as I have not had extensive experience vetting the possible *gotchas* with this configuration (i.e. calling the `vagrant` command via python **subprocess**)
- As with any piece of automation, you can do some serious damage given the right set of commands and functions.
- Please, for the love of FSM, make sure you know what you're doing 😎
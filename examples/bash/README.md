<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Bash Example](#bash-example)
- [Exercises](#exercises)
  - [Obtain Project Files](#obtain-project-files)
  - [Ping Google Function](#ping-google-function)
- [Learning Points](#learning-points)
- [Caveats](#caveats)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<a name="bash-example"></a>
# Bash Example

The Tasksfile here consists of an ansible playbook that has been repurposed as a bastardized bash script.

Essentially, it's a stripped down ansible playbook that holds bash functions represented in YAML syntax.

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
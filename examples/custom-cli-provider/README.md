<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Custom CLI Provider Example](#custom-cli-provider-example)
- [Exercises](#exercises)
  - [Install and Obtain Project Files](#install-and-obtain-project-files)
  - [Display Usage](#display-usage)
- [Learning Points](#learning-points)
- [Caveats](#caveats)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<a name="custom-cli-provider-example"></a>
# Custom CLI Provider Example

**Note**: This exercise only works with python 3 (for now)
**TODO**: Refactor plugin logic to work with python version 2.x

Here we employ a custom cli-provider named _example_

The cli-provider is located in the [plugins](plugins) directory adjacent to this document.

The Taskfile here consists of an ansible playbook that has been repurposed as a bastardized bash script.

Essentially, it's a stripped down ansible playbook that holds bash functions represented in YAML syntax.

The exercise here showcases how one can extend the functionality of `tasks`, the ansible task runner command
through the use of custom cli-provider plugins.

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
cd ansible-taskrunner/exercises/custom-cli-provider
```
<a name="display-usage"></a>
## Display Usage

* Let's review the output of the the `run` subcommand help<br />
```
tasks run --help
```

You should see `--this-is-an-example-switch` in the option listing.

This switch is made available through the use of a custom cli provider plugin located in the plugins folder adjacent to this README.

As such, you can get creative by adjusting the plugin's `invocation` function. 

It's all python, so code away to your heart's content: [example](plugins/providers/example)

<a name="learning-points"></a>
# Learning Points

- You are able to easily adjust cli options for your YAML-organized Bash script :)
- You are able to override the default handler for command and cli-options through a plugin system
- You can get pretty creative with how you proceed with this approach

<a name="caveats"></a>
# Caveats

- Again, the plugin system is only working for python 3, so don't expect this to work if your python version is 2.x.
- As with any piece of automation, you can do some serious damage given the right set of commands and functions.
- Please, for the love of FSM, make sure you know what you're doing 😎
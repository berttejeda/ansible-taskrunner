<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Ansible Example](#ansible-example)
- [Exercises](#exercises)
  - [Obtain Project Files](#obtain-project-files)
  - [Mock Test](#mock-test)
  - [Copy file(s) to target host](#copy-files-to-target-host)
  - [Equivalent ansible-playbook command](#equivalent-ansible-playbook-command)
- [Learning Points](#learning-points)
- [Caveats](#caveats)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<a name="ansible-example"></a>
# Ansible Example

The Tasksfile here is an ansible playbook that copies a file/directory to a destination path on the target machine(s).

<a name="exercises"></a>
# Exercises

<a name="obtain-project-files"></a>
## Obtain Project Files

* Download the latest [release](https://github.com/berttejeda/ansible-taskrunner/releases)<br />
* Clone the git repository and navigate to the example<br />

```
git clone https://github.com/berttejeda/ansible-taskrunner.git
cd ansible-taskrunner/exercises/ansible
```

<a name="mock-test"></a>
## Mock Test

* Let's run the `mock_test` embedded function<br />
```
tasks run -h localhost -p test -t /tmp --mock
```

<a name="copy-files-to-target-host"></a>
## Copy file(s) to target host

* Try a typical use case<br />
```
mkdir -p ${HOME}/some/directory
tasks run -h some-host.somedomain -p ${HOME}/some/directory -t /tmp
```

<a name="equivalent-ansible-playbook-command"></a>
## Equivalent ansible-playbook command

* Let's echo the underlying ansible command<br />
```
tasks run -h localhost -p ${HOME}/some/directory -t /tmp --echo
```

* The output should be similar to:<br />

```
ansible-playbook ${__ansible_extra_options} -i /tmp/ansible-inventoryrUXgPX.tmp.ini -e target_hosts="localhost" -e echo="True" -e target_path="/tmp" -e local_path="/home/vagrant/some/directory" -e parameter_set=False   Taskfile.yaml
```

The above command makes use of an ephemeral inventory file that is dynamically created at runtime.
Let's adjust the above by utilizing an inline inventory specification instead, as follows:

```
mkdir -p ${HOME}/some/directory
ansible-playbook ${__ansible_extra_options} -i localhost, -e target_hosts="localhost" -e echo="True" -e target_path="/tmp" -e local_path="/home/vagrant/some/directory" -e parameter_set=False   Taskfile.yaml
```

<a name="learning-points"></a>
# Learning Points

- You are able to launch the `ansible-playbook` command using a meta step that makes it trivial to alter playbook execution behavior
- Easily adjust commandline options (just shuffle things around in yaml)
- Much easier than running the `ansible-playbook` with a long list of `--extra-vars` (`-e`)

<a name="caveats"></a>
# Caveats

- The example here is strictly for elucidating what's really happening under the hood, so to speak.
- I shy away from playbooks with an 'all' _hosts_ designation.
- As with any piece of automation, you can do some serious damage given the right set of tasks.
- Please, for the love of FSM, make sure you know what you're doing 😎
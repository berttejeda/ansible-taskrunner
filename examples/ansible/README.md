<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Ansible Example](#ansible-example)
- [Exercises](#exercises)
  - [Install and Obtain Project Files](#install-and-obtain-project-files)
  - [Display Usage](#display-usage)
  - [Mock Test](#mock-test)
  - [Copy file(s) to target host](#copy-files-to-target-host)
  - [Equivalent ansible-playbook command](#equivalent-ansible-playbook-command)
- [Learning Points](#learning-points)
- [Caveats](#caveats)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<a name="ansible-example"></a>
# Ansible Example

The Taskfile here is an ansible playbook that copies a file/directory to a destination path on the target machine(s).

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
cd ansible-taskrunner/exercises/ansible
```

<a name="display-usage"></a>
## Display Usage

`tasks run --help`

```
Copy local file(s)/folder(s) from local to target host(s)

Options:
  --version                Show the version and exit.
  ---make, ---m TEXT       Call shell function
  ---raw TEXT              Specify raw options for underlying subprocess
  ---echo                  Don't run, simply echo underlying commands
  --mock                   Invoke the 'mock_test' shell function
  -p, --local-path TEXT    Local path you're copying from  [required]
  -t, --target-path TEXT   Target path on host you're copying files to
                           [required]
  -h, --target-hosts TEXT  Target host you're copying files to  [required]
  ---inventory, ---i TEXT  Override embedded inventory specification
  ---debug, ---d TEXT      Start task run with ansible in debug mode
  --help                   Show this message and exit.


After playbook run, the specified file system objects should
be mirrored onto the target host(s)

Examples:
- You want to synchronize files to your target hosts:
tasks run -p myfolder -h host1 -t /data
- You want to synchronize mock data:
tasks run -p myfolder -h host1 -t /data --mock

Available shell functions:
mock_test: Create mock data and invoke playbook
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
tasks run -h localhost -p ${HOME}/some/directory -t /tmp ---echo
```

* The output should be similar to:<br />

```
if [[ ($inventory) && ( 'True' == 'True') ]];then
echo -e """[target_hosts]
$(echo -e "${target_hosts}" | tr ',' '\n')
[all_hosts:children]
target_hosts
""" | while read line;do
eval "echo -e ${line}" >> "/tmp/ansible-inventoryrUXgPX.tmp.ini"
done
fi

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
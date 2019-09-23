SAMPLE_CONFIG = '''
---
cli:
  providers:
    default: ansible
...
'''

SAMPLE_SFTP_CONFIG = '''
{
    "type": "sftp",
    "save_before_upload": true,
    "upload_on_save": true,
    "sync_down_on_open": false,
    "sync_skip_deletes": false,
    "sync_same_age": true,
    "confirm_downloads": false,
    "confirm_sync": true,
    "confirm_overwrite_newer": false,
    "host": "CHANGEME",
    "user": "CHANGEME",
    "ssh_key_file": "CHANGEME",
    "port": "22",
    "remote_path": "CHANGEME",
    "ignore_regexes": [
        "\\\\.sublime-(project|workspace)", "sftp-config(-alt\\\\d?)?\\\\.json",
        "sftp-settings\\\\.json", "/venv/", "\\\\.svn/", "\\\\.hg/", "\\\\.git/",
        "\\\\.bzr", "_darcs", "CVS", "\\\\.DS_Store", "Thumbs\\\\.db", "desktop\\\\.ini"
    ],
    "connect_timeout": 30
}
'''

SAMPLE_TASKS_MANIFEST = '''
- hosts: myhosts
  gather_facts: true
  become: true
  vars:
    myvar1: myvalue1
    myvar2: myvalue2
    myvar3: myvalue3
    myvar4: |
      This is a multiline value
      of type string
    myvar5:
      - mylistvalue1
      - mylistvalue2
      - mylistvalue3
      - mylistvalue4
    required_parameters:
      aws:
        -d|--db-hosts: dbhosts_aws
        -a|--some-special-aws-flag: aws_flag
      gcp:
        -d|--db-hosts: dbhosts_gcp
        -g|--some-special-gcp-flag: gcp_flag
      -d|--db-hosts: dbhosts
      -w|--web-hosts: webhosts
      -t|--some-parameter: some_value
    optional_parameters:
      -l|--another-parameter: another_value
      -A: hello
      -PR: preflight_and_run
      --debug-mode: debug_mode
    help:
      message: |
        Do something against db and web hosts
      epilog: |
        This line will be displayed at the end of the help text readme
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
      preflight_and_run:
        shell: bash
        source: |-
          echo 'Running Preflight Tasks!'
          tasks run -d dbhost1 -w webhost1 -t value1
  tasks:
    - debug:
        msg: |
          Hello from Ansible!
          You specified: {{ some_value }}
          You specified: {{ another_value }}
'''

# Imports
import logging
import json
import os
from os import fdopen, remove
import re
import uuid
import sys
import time
from tempfile import mkstemp

provider_name = 'ansible'

# Setup Logging
logger = logging.getLogger(__name__)
if '--debug run' in ' '.join(sys.argv):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

if getattr(sys, 'frozen', False):
    # frozen
    self_file_name = os.path.basename(sys.executable)
else:
    self_file_name = os.path.basename(__file__)    

# Import third-party and custom modules
try:
    import click
    from libs.formatting import ansi_colors, Struct
    from libs.proc_mgmt import shell_invocation_mappings
    from libs.proc_mgmt import CLIInvocation
except ImportError as e:
    print('Error in %s ' % os.path.basename(self_file_name))
    print('Failed to import at least one required module')
    print('Error was %s' % e)
    print('Please install/update the required modules:')
    print('pip install -U -r requirements.txt')
    sys.exit(1)


class ProviderCLI:
    def __init__(self, parameter_set=None, vars_input=None):
        if vars_input is None:
            vars_input = {}
        self.vars = vars_input
        self.parameter_set = parameter_set
        self.logger = logger
        pass

    @staticmethod
    def options(func):
        """Add provider-specific click options"""
        option = click.option('---debug', type=str, help='Start task run with ansible in debug mode',
                              default=False, required=False)
        func = option(func)
        option = click.option('---inventory', is_flag=False, help='Override embedded inventory specification',
                              required=False)
        func = option(func)
        return func
    
    def invoke_bastion_mode(self, bastion_settings, invocation, remote_command):
        """Execute the underlying subprocess via a bastion host"""
        logger.info('Engage Bastion Mode')
        paramset = invocation.get('param_set')
        bastion = Struct(**bastion_settings)
        logger.info('Checking for SFTP config file %s' % bastion.config_file)
        if os.path.exists(bastion.config_file):
            logger.info('Reading %s' % bastion.config_file)
            try:
                # Read the Sublime Text 3-compatible sftp config file
                file_contents = open(bastion.config_file).readlines()
                # Ignore comments
                file_contents_no_comments = [l.strip() for l in file_contents if not l.strip().startswith('/') and l.strip()]
                # Account for last line possibly ending in ','
                penultimate_line = file_contents_no_comments[-2]
                if penultimate_line.endswith(','):
                    file_contents_no_comments = [penultimate_line.strip(',') if l==penultimate_line else l for l in file_contents_no_comments]
                file_contents_no_comments = '\n'.join(file_contents_no_comments)
                settings = Struct(**json.loads(file_contents_no_comments))
            except Exception as e:
                logger.error('I trouble reading {c}, error was "{err}"'.format(
                    c=bastion.config_file,
                    err=e)
                )
                sys.exit(1)
        else:
            logger.error("Could not find %s, please run 'tasks init --help'" % bastion.config_file)
            sys.exit(1)
        # Import third-party and custom modules
        try:
            from libs.proc_mgmt import Remote_CLIInvocation
            from libs.sshutil.client import SSHUtilClient
        except ImportError as e:
            print('Error in %s ' % os.path.basename(self_file_name))
            print('Failed to import at least one required module')
            print('Error was %s' % e)
            print('Please install/update the required modules:')
            print('pip install -U -r requirements.txt')
            sys.exit(1)            
        ssh_client = SSHUtilClient(settings)
        sftp_sync = ssh_client.sync()
        remote_sub_process = Remote_CLIInvocation(settings, ssh_client)
        local_dir = os.getcwd().replace('\\', '/')
        local_dir_name = os.path.basename(os.getcwd().replace('\\', '/'))
        remote_dir = settings.remote_path
        logger.info('Checking remote path %s' % remote_dir)
        cmd = 'echo $(test -d {0} && echo 1 || echo 0),$(cd {0} 2>/dev/null && git status 1> /dev/null 2> /dev/null && echo 1 || echo 0)'.format(remote_dir)
        # Check whether the remote path exists and is a git repo
        rmc = remote_sub_process.call(remote_dir, cmd) or ['0']
        rms = sum([int(n) for n in ''.join(rmc).split(',')])
        rem_exists = True if rms > 0 else False
        loc_is_git = True if os.path.exists('.git') else False
        rem_is_git = True if rms == 2 else False
        if rem_is_git:
            logger.info('OK, remote path exists and is a git repo')
        elif rem_exists:
            logger.info('OK, remote path exists')
        else:            
            cmd = 'mkdir -p %s' % remote_dir
            mkdir_result = remote_sub_process.call('/', cmd)
            if mkdir_result:
                logger.info("Performing initial sync to %s ..." % remote_dir)
                sftp_sync.to_remote('.', remote_dir)
                rem_exists = True
            else:
                logger.error('Unable to create remote path!')
                sys.exit(1)                
        logger.info('Checking for locally changed files ...')
        if loc_is_git:
            cmd = 'git diff-index --name-only HEAD -- && git ls-files --others --exclude-standard'
            local_changed = os.popen(cmd).readlines()
        else:
            # If local path is not a git repo then
            # we'll only sync files in the current working directory
            # that have changed within the last 5 minutes
            _dir = os.getcwd()
            exclusions = ['sftp-config.json']
            local_changed = list(fle for rt, _, f in os.walk(_dir) for fle in f if time.time() - os.stat(os.path.join(rt, fle)).st_mtime < 300 and f not in exclusions)
        logger.info('Checking for remotely changed files ...')
        no_clobber = settings.get('at_no_clobber')
        if rem_is_git:
            remote_changed = remote_sub_process.call(remote_dir, cmd)
            if remote_changed:
                if no_clobber:
                    to_sync = list(set(local_changed) - set(remote_changed))
                else:
                    to_sync = list(set(local_changed))
            else:
                logger.error('There was a problem checking for remotely changed files')
                sys.exit(1)
        else:
            to_sync = list(set(local_changed))
        if len(to_sync) > 0:
            logger.info("Performing sync to %s ..." % remote_dir)
        for path in to_sync:
            dirname = os.path.dirname(path)
            filename = os.path.basename(path).strip()
            _file_path = os.path.join(dirname, filename)
            file_path = _file_path.replace('\\','/')
            _remote_path = os.path.join(remote_dir, file_path)
            remote_path = os.path.normpath(_remote_path).replace('\\','/')
            logger.debug('Syncing {} to remote {}'.format(file_path, remote_path))
            sftp_sync.to_remote(file_path, remote_path)
        # Derive remote command 
        # (accounting for parameter sets)
        if paramset:
            for p in enumerate(paramset):
                sys.argv.insert(p[0] + 1, p[1])
        # remote_command = ' '.join([a for a in sys.argv if a != '---bastion-mode'][1:])
        # tasks_file_override = invocation.get('tasks_file_override')
        # if tasks_file_override:
        #     remote_command = 'tasks -f {} {}'.format(tasks_file_override, remote_command)
        # else:
        #     remote_command = 'tasks {}'.format(remote_command)
        remote_command_result = remote_sub_process.call(remote_dir, remote_command, stdout_listen=True)
        if remote_command_result.returncode > 0:
            logger.error('Remote command failed with: %s' % ' '.join(remote_command_result.stderr))
            sys.exit(1)
        else:
            return remote_command_result

    def invocation(self,
                   args=None,
                   bastion_settings={},
                   bash_functions=[],
                   cli_vars='',
                   debug=False,
                   default_vars={},
                   invocation={},
                   kwargs={},
                   list_vars=[],
                   paramset_var=None,
                   prefix='',
                   raw_args='',
                   string_vars=[],
                   yaml_input_file=None,
                   yaml_vars={}):
        """Invoke commands according to provider"""
        logger.info('Ansible Command Provider')
        ansible_playbook_command = default_vars.get(
            'ansible_playbook_command', 'ansible-playbook')
        # Embedded inventory logic
        embedded_inventory = False
        trap = ''
        inventory_input = kwargs.get('_inventory')
        embedded_inventory_string = yaml_vars.get('inventory')
        if not inventory_input and not embedded_inventory_string:
            logger.error(
                "Playbook does not contain an inventory declaration and no inventory was specified. Seek --help")
            sys.exit(1)
        elif inventory_input:
            ans_inv_fp = inventory_input
            ans_inv_fso_desc = None
            logger.info("Using specified inventory file %s" % ans_inv_fp)
            if bastion_settings.get('enabled'):
                if not debug:
                    trap = 'trap "rm -f %s" EXIT' % ans_inv_fp            
        else:
            if bastion_settings.get('enabled'):
                ans_inv_fp = '/tmp/ansible.inventory.%s.tmp.ini' % str(uuid.uuid4())
                ans_inv_fso_desc = None
                if not debug:
                    trap = 'trap "rm -f %s" EXIT' % ans_inv_fp
            else:
                ans_inv_fso_desc, ans_inv_fp = mkstemp(prefix='ansible-inventory', suffix='.tmp.ini')                 
                logger.info("No inventory specified")
                logger.info("Created temporary inventory file %s (normally deleted after run)" % ans_inv_fp)
            inventory_input = embedded_inventory_string
            embedded_inventory = True
        ansible_extra_options = [
            '-e {k}="{v}"'.format(k=key, v=value) for key, value in kwargs.items() if value]
        # Append our default values to the set of ansible extra options
        ansible_extra_options = ansible_extra_options + [
            '-e {k}="{v}"'.format(k=key, v=value) for key, value in default_vars.items() if value]
        # Append the parameter sets var to the set of ansible extra options
        ansible_extra_options.append('-e %s' % paramset_var)
        # Build command string
        if ans_inv_fso_desc or bastion_settings.get('enabled'):
            inventory_command = '''
{tr}

if [[ ($inventory) && ( '{emb}' == 'True') ]];then
  echo -e """{ins}""" | while read line;do
      eval "echo -e ${{line}}" >> "{inf}"
  done
fi
'''.format(
        tr=trap,
        emb=embedded_inventory,
        ins=inventory_input,
        inf=ans_inv_fp,
        )
        else:
            inventory_command = ''
        pre_commands = '''{anc}
{clv}
{dsv}
{dlv}
{bfn}
    {inc}'''.format(
                anc=ansi_colors.strip(),
                dlv='\n'.join(list_vars),
                dsv='\n'.join(string_vars),
                clv=cli_vars.strip(),
                bfn='\n'.join(bash_functions),
                inc=inventory_command,
                deb=debug
            )
        ansible_command = '''
    {apc} ${{__ansible_extra_options}} -i {inf} {opt} {arg} {raw} {ply}
'''.format(
                apc=ansible_playbook_command,
                inf=ans_inv_fp,
                opt=' '.join(ansible_extra_options),
                ply=yaml_input_file,
                arg=args,
                raw=raw_args
            )
        command = pre_commands + ansible_command
        # Command invocation
        # Bastion host logic
        if prefix == 'echo':
            if debug:
                print(pre_commands)
                print(ansible_command)
            else:
                print(inventory_command)
                print(ansible_command)
        else:
            if bastion_settings.get('enabled'):
                self.invoke_bastion_mode(bastion_settings, invocation, command)
            else:
                sub_process = CLIInvocation()
                sub_process.call(command, debug_enabled=debug)
        # Debugging
        if debug:
            ansible_command_file_descriptor, ansible_command_file_path = mkstemp(prefix='ansible-command',
                                                                                 suffix='.tmp.sh')
            logger.debug('Ansible command file can be found here: %s' %
                         ansible_command_file_path)
            logger.debug('Ansible inventory file can be found here: %s' %
                         ans_inv_fp)
            with fdopen(ansible_command_file_descriptor, "w") as f:
                f.write(command)
        else:
            if ans_inv_fso_desc:
                os.close(ans_inv_fso_desc)
                remove(ans_inv_fp)

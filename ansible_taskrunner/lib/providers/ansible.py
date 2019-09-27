# Imports
import logging
import json
import os
from os import fdopen, remove
import re
import sys
from tempfile import mkstemp

provider_name = 'ansible'

# Setup Logging
logger = logging.getLogger(__name__)
if '--debug run' in ' '.join(sys.argv):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# Import third-party and custom modules
try:
    import click
    from formatting import ansi_colors, Struct
    from proc_mgmt import shell_invocation_mappings
    from proc_mgmt import CLIInvocation
except ImportError as e:
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
    
    def invoke_bastion_mode(self, bastion_settings):
        """Execute the underlying subprocess via a bastion host"""
        logger.info('Engage Bastion Mode')
        bastion = Struct(**bastion_settings)
        logger.info('Checking for SFTP config file %s' % bastion.config_file)
        if os.path.exists(bastion.config_file):
            logger.info('Reading %s' % bastion.config_file)
            try:
                settings = Struct(**json.loads(open(bastion.config_file).read()))
            except Exception as e:
                logger.error('I trouble reading {c}, error was "{err}"'.format(
                    c=bastion.config_file,
                    err=e)
                )
                sys.exit(1)
        else:
            logger.error('Could not find %s, seek --help' % bastion.config_file)
            sys.exit(1)
        # Import third-party and custom modules
        try:
            from proc_mgmt import Remote_CLIInvocation
            from sshutil.client import SSHUtilClient
        except ImportError as e:
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
        remote_dir = '{}'.format(settings.remote_path)
        remote_git_dir = '{}/{}'.format(remote_dir, local_dir_name)
        logger.info('Checking remote path %s' % remote_git_dir)
        cmd = 'echo $(test -d {0} && echo 1 || echo 0),$(cd {0} 2>/dev/null && git status 1> /dev/null 2> /dev/null && echo 1 || echo 0)'.format(remote_git_dir)
        rmc = remote_sub_process.call(remote_dir, cmd)
        rms = sum([int(n) for n in ''.join(rmc).split(',')])
        rem_exists = True if rms > 0 else False
        loc_is_it = True if os.path.exists('.git') else False
        rem_is_git = True if rms == 2 else False
        if rem_is_git:
            logger.info('OK, remote path exists and is a git repo')
        elif rem_exists:
            logger.info('OK, remote path exists')
        else:            
            cmd = 'mkdir -p %s' % remote_git_dir
            mkdir = remote_sub_process.call('/', cmd)
            if mkdir:
                logger.info("Performing initial sync to %s ..." % remote_git_dir)
                sftp_sync.to_remote(local_dir, remote_git_dir)
            rem_exists = True                
        logger.info('Checking for locally changed files ...')
        if loc_is_it:
            cmd = 'git diff-index --name-only HEAD -- && git ls-files --others --exclude-standard'
            local_changed = os.popen(cmd).readlines()
        else:
            local_changed = [f for f in os.listdir('.') if os.path.isfile(f)]
        logger.info('Checking for remotely changed files ...')
        no_clobber = settings.get('at_no_clobber')
        if rem_is_git:
            remote_changed = remote_sub_process.call(remote_git_dir, cmd)
            if remote_changed:
                if no_clobber:
                    to_sync = list(set(local_changed) - set(remote_changed))
                else:
                    to_sync = list(set(local_changed))
            else:
                logger.error('There was a problem checking for remotely changed files')
                sys.exit(1)
        elif rem_exists:
            to_sync = list(set(local_changed))
        logger.info("Performing sync to %s ..." % remote_git_dir)
        for path in to_sync:
            dirname = os.path.dirname(path)
            filename = os.path.basename(path)
            _file_path = os.path.join(dirname, filename)
            file_path = os.path.normpath(_file_path).replace('\\','/')
            _remote_path = os.path.join(remote_git_dir, file_path)
            remote_path = os.path.normpath(_remote_path).replace('\\','/')
            logger.debug('Syncing {} to remote {}'.format(file_path, remote_path))
            sftp_sync.to_remote(file_path, remote_path)
        remote_command = ' '.join([a for a in sys.argv if a != '---bastion-mode'])
        remote_sub_process.call(remote_git_dir, remote_command, stdout_listen=True)
        return        

    def invocation(self, yaml_input_file=None,
                   string_vars=[],
                   default_vars={},
                   paramset_var=None,
                   bash_functions=[],
                   cli_vars='',
                   yaml_vars={},
                   list_vars=[],
                   debug=False,
                   args=None,
                   prefix='',
                   raw_args='',
                   bastion_settings={},
                   kwargs={}):
        """Invoke commands according to provider"""
        logger.info('Ansible Command Provider')
        # Bastion host logic
        if bastion_settings.get('enabled') and prefix !='echo':
            self.invoke_bastion_mode(bastion_settings)
        else:        
            sub_process = CLIInvocation()
            ansible_playbook_command = default_vars.get(
                'ansible_playbook_command', 'ansible-playbook')
            # Embedded inventory logic
            embedded_inventory = False
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
            else:
                ans_inv_fso_desc, ans_inv_fp = mkstemp(prefix='ansible-inventory', suffix='.tmp.ini')                 
                logger.info("No inventory specified")
                logger.info("Writing a temporary inventory file %s (normally deleted after run)"
                            % ans_inv_fp)
                inventory_input = embedded_inventory_string
                embedded_inventory = True
            ansible_extra_options = [
                '-e {k}="{v}"'.format(k=key, v=value) for key, value in kwargs.items() if value]
            ansible_extra_options.append('-e %s' % paramset_var)
            # Build command string
            if ans_inv_fso_desc:
                inventory_command = '''
if [[ ($inventory) && ( '{emb}' == 'True') ]];then
  echo -e """{ins}""" | while read line;do
      eval "echo -e ${{line}}" >> "{inf}"
  done
fi
                '''.format(
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
            if prefix == 'echo':
                if debug:
                    print(pre_commands)
                    print(ansible_command)
                else:
                    print(inventory_command)
                    print(ansible_command)
            else:
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

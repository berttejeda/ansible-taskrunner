# Imports
import logging
import os
from os import fdopen, remove
import sys
from tempfile import mkstemp

provider_name = 'ansible'

# Logging
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)

# Import third-party and custom modules
try:
    import click
    from formatting import ansi_colors, reindent
    from yamlc import CLIInvocation
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
        option = click.option('---debug', '---d', type=str, help='Start task run with ansible in debug mode',
                              default=False, required=False)
        func = option(func)
        option = click.option('---inventory', '---i', is_flag=False, help='Override embedded inventory specification',
                              required=False)
        func = option(func)
        return func

    @staticmethod
    def invocation(yaml_input_file=None,
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
                   kwargs={}):
        """Invoke commands according to provider"""
        logger.info('Ansible Command Provider')
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
            ansible_inventory_file_path = inventory_input
            ansible_inventory_file_path_descriptor = None
        else:
            ansible_inventory_file_path_descriptor, ansible_inventory_file_path = mkstemp(prefix='ansible-inventory',
                                                                                          suffix='.tmp.ini')
            logger.info("No inventory specified")
            logger.info("Writing a temporary inventory file %s (normally deleted after run)"
                        % ansible_inventory_file_path)
            inventory_input = embedded_inventory_string
            embedded_inventory = True
        ansible_extra_options = [
            '-e {k}="{v}"'.format(k=key, v=value) for key, value in kwargs.items() if value]
        ansible_extra_options.append('-e %s' % paramset_var)
        # Build command string
        inventory_command = '''
            if [[ ($inventory) && ( '{emb}' == 'True') ]];then
              echo -e """{ins}""" | while read line;do
                  eval "echo -e ${{line}}" >> "{inf}"
              done
            fi
            '''.format(
                emb=embedded_inventory,
                ins=inventory_input,
                inf=ansible_inventory_file_path,
                )
        inventory_command = reindent(inventory_command,0)
        pre_commands = '''
        {anc}
        {dsv}
        {dlv}
        {clv}
        {bfn}
        {inc}
        '''.format(
            anc=ansi_colors,
            dlv='\n'.join(list_vars),
            dsv='\n'.join(string_vars),
            clv=cli_vars,
            bfn='\n'.join(bash_functions),
            inc=inventory_command,
            deb=debug
        )
        ansible_command = '''
        {apc} ${{__ansible_extra_options}} -i {inf} {opt} {arg} {raw} {ply}
        '''.format(
            apc=ansible_playbook_command,
            inf=ansible_inventory_file_path,
            opt=' '.join(ansible_extra_options),
            ply=yaml_input_file,
            arg=args,
            raw=raw_args
        )
        command = reindent(pre_commands + ansible_command, 0)
        # Command invocation
        if prefix == 'echo':
            if debug:
                print(pre_commands)
                print(ansible_command)
            else:
                print(inventory_command)
                print(ansible_command)
        else:
            CLIInvocation().call(command)
        # Debugging
        if debug:
            ansible_command_file_descriptor, ansible_command_file_path = mkstemp(prefix='ansible-command',
                                                                                 suffix='.tmp.sh')
            logger.debug('Ansible command file can be found here: %s' %
                         ansible_command_file_path)
            logger.debug('Ansible inventory file can be found here: %s' %
                         ansible_inventory_file_path)
            with fdopen(ansible_command_file_descriptor, "w") as f:
                f.write(command)
        else:
            if ansible_inventory_file_path_descriptor:
                os.close(ansible_inventory_file_path_descriptor)
                remove(ansible_inventory_file_path)

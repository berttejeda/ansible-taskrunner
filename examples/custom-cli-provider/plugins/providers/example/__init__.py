# Imports
import json
import logging
import re
import sys

provider_name = 'example'

# Setup Logging
logger = logging.getLogger(__name__)
if '--debug run' in ' '.join(sys.argv):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# Import third-party and custom modules
try:
    if sys.version_info[0] >= 3:
        from lib.py3 import click
    else:
        from lib.py2 import click
    from lib.proc_mgmt import shell_invocation_mappings
    from lib.proc_mgmt import CLIInvocation    
except ImportError as e:
    print('Failed to import at least one required module')
    print('Error was %s' % e)
    print('Please install/update the required modules:')
    print('pip install -U -r requirements.txt')
    sys.exit(1)

class ProviderCLI():
    def __init__(self, parameter_set=None, vars_input={}):
        self.vars = vars_input
        self.parameter_set = parameter_set
        self.logger = logger
        pass

    def options(self, func):
        option = click.option('--this-is-an-example-switch', is_flag = True, default=False, required=False)
        func = option(func)
        return func

    def invocation(self, args=None,
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
        logger.info('Example Command Provider')
        sub_process = CLIInvocation()
        command = '''{dsv}
{dlv}
{clv}
{bfn}
        '''.format(
            dlv='\n'.join(list_vars),
            dsv='\n'.join(string_vars),
            clv=cli_vars,
            bfn='\n'.join(bash_functions),
            deb=debug
        )
        command = command
        # Command invocation
        if prefix == 'echo':
            logger.info("ECHO MODE ON")
            print(command)
        else:
            sub_process.call(command)
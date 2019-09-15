# Imports
import json
import logging
import re
import sys

provider_name = 'example'

# Logging
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)

# Import third-party and custom modules
try:
    if sys.version_info[0] >= 3:
        from lib.py3 import click
    else:
        from lib.py2 import click
    from lib.common.yamlc import CLIInvocation
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

    def invocation(self, 
        yaml_input_file=None, 
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
        logger.info('Example Command Provider')
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
            CLIInvocation().call(command)
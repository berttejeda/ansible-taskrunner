# Imports
import logging
import sys

provider_name = 'bash'

# Logging
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)

# Import third-party and custom modules
try:
    import click
    from .. import reindent
    from .. import YamlCLIInvocation
except ImportError as e:
    print('Failed to import at least one required module')
    print('Error was %s' % e)
    print('Please install/update the required modules:')
    print('pip install -U -r requirements.txt')
    sys.exit(1)


class ProviderCLI:
    def __init__(self, parameter_set=None, vars_input={}):
        self.vars = vars_input
        self.parameter_set = parameter_set
        self.logger = logger
        pass

    @staticmethod
    def options(func):
        """Add provider-specific click options"""
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
        logger.info('Bash Command Provider')
        command = '''
        {dsv}
        {psv}
        {dlv}
        {clv}
        {bfn}
        '''.format(
            dlv='\n'.join(list_vars),
            dsv='\n'.join(string_vars),
            psv=paramset_var,
            clv=cli_vars,
            bfn='\n'.join(bash_functions),
            deb=debug
        )
        command = reindent(command, 0)
        # Command invocation
        if prefix == 'echo':
            logger.info("ECHO MODE ON")
            print(command)
        else:
            YamlCLIInvocation().call(command)

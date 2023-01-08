# Imports
import logging
import os
import sys

provider_name = 'bash'

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
    from ansible_taskrunner.libs.proc_mgmt import shell_invocation_mappings
    from ansible_taskrunner.libs.proc_mgmt import CLIInvocation
except ImportError as e:
    print('Error in %s ' % os.path.basename(self_file_name))
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
    def invocation(args=None,
                   bastion_settings={},
                   shell_functions=[],
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
                   suppress_output=False,
                   yaml_input_file=None,
                   yaml_vars={}):
        """Invoke commands according to provider"""
        logger.debug('Bash Command Provider')
        sub_process = CLIInvocation()
        command = '''
{clv}
{dsv}
{psv}
{dlv}
{bfn}
        '''.format(
            dlv='\n'.join(list_vars),
            dsv='\n'.join(string_vars),
            psv=paramset_var,
            clv=cli_vars,
            bfn='\n'.join(shell_functions),
            deb=debug
        )
        command = command
        # Command invocation
        if prefix == 'echo':
            logger.info("ECHO MODE ON")
            print(command)
        else:
            result = sub_process.call(command, debug_enabled=debug, suppress_output=suppress_output)
            sys.exit(result.returncode)

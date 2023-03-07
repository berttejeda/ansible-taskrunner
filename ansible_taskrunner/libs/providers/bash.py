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

from ansible_taskrunner.libs.proc_mgmt import CLIInvocation

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

    def invocation(self, **kwargs):
        """Invoke commands according to provider"""

        args = kwargs.get('args')
        bastion_settings = kwargs.get('bastion_settings',{})
        shell_functions = kwargs.get('shell_functions', [])
        cli_functions = kwargs.get('cli_functions')
        cli_vars = kwargs.get('cli_vars', '')
        debug = kwargs.get('debug', False)
        default_vars = kwargs.get('default_vars', {})
        invocation = kwargs.get('invocation', {})
        list_vars = kwargs.get('list_vars', [])
        paramset_var = kwargs.get('paramset_var')
        prefix = kwargs.get('prefix', '')
        raw_args = kwargs.get('raw_args', '')
        string_vars = kwargs.get('string_vars', [])
        suppress_output = kwargs.get('suppress_output', False)
        yaml_input_file = kwargs.get('yaml_input_file')
        yaml_vars = kwargs.get('yaml_vars', {})
        provider_vars = kwargs.get('provider_vars', {})
        provider_vars_string_block = kwargs.get('provider_vars_string_block', '')
        sub_process = CLIInvocation()

        logger.debug('Bash CLI Provider')

        # Command invocation
        if cli_functions:
            cf = '\n'.join(cli_functions)
            command = f"{provider_vars_string_block}\n{shell_functions}\n{cf} {args} {raw_args}"
            if prefix == 'echo':
                print(command)
                sys.exit(0)
            else:
                if sub_process:
                    sub_process.call(command, debug_enabled=debug, suppress_output=suppress_output)
                    return
                else:
                    logger.error('No subprocess defined for this provider')


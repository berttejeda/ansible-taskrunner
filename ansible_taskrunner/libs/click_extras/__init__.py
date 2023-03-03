# Imports
import click
import sys
from ansible_taskrunner.logger import Logger
from bertdotconfig.configutils import AttrDict

from ansible_taskrunner.libs.click_extras.options_processor import ExtendCLIOptionsProcessor

logger_obj = Logger()
logger = logger_obj.init_logger(__name__)

class ExtendCLI(ExtendCLIOptionsProcessor):

    def __init__(self, **kwargs):

        self.parameter_set = kwargs.get('parameter_set')
        global_options = kwargs.get('global_options', {})
        self.command_vars = kwargs.get('command_vars', {})
        # Merge in global options
        AttrDict.merge(self.command_vars, {'options': global_options})
        self.help_msg_map = kwargs.get('help_msg_map', {})
        self.available_vars = kwargs.get('available_vars', {})
        # Populate list of available variables for use in internal string Templating
        self.sys_platform = sys.platform
        self.seen_options = set()

    def bastion_mode(self, func):
        """
        Explicity define command-line options for bastion mode operation
        """
        option = click.option('---bastion-mode',
                      is_flag=True,
                      help='Force execution of commands via a bastion host')
        func = option(func)
        # Determine if bastion host is a required parameter
        if len(sys.argv) > 0 and sys.argv[0] == 'init':
            bastion_host_required = True if sys.argv[0] == 'init' else False
        elif len(sys.argv) > 1:
            bastion_host_required = True if sys.argv[1] == 'init' else False
        else:
            bastion_host_required = False
        # Determine if bastion mode is forced
        force_bastion_mode = True if '---bastion-mode' in sys.argv else False
        if sys.platform in ['win32', 'cygwin'] or force_bastion_mode:
            option = click.option('---bastion-host','-h',
                         help='Specify bastion host',
                         required=bastion_host_required)
            func = option(func)
            option = click.option('---bastion-host-port','-p',
                         help='Specify bastion host port')
            func = option(func)
            option = click.option('---bastion-user','-u',
                         help='Override default username')
            func = option(func)
            option = click.option('---bastion-remote-path','-r',
                          help='Specify remote workspace')
            func = option(func)
            option = click.option('---bastion-ssh-key-file','-k',
                          help='Override default ssh key file')
            func = option(func)
        return func

    def options(self, func):
        """
        Read dictionary of parameters, append these
        as additional options to incoming click function
        """
        required_parameters = self.command_vars.get('options.required', {})
        if not required_parameters:
            required_parameters = {}
        else:
            param_list = list(required_parameters.items())
            # Filter out any None/Null values
            # Accounting for mutually exclusive options
            for param in param_list:
                if param[0] != 'or' and param[1] is None:
                    logger.debug(f"Removing invalid option key '{param[0]}'")
                    required_parameters.pop(param[0])
        extended_cli_func_required = self.process_options(
            required_parameters, func, is_required=True)
        optional_parameters = self.command_vars.get('options.optional', {})
        if not optional_parameters:
            optional_parameters = {}
        else:
            param_list = list(optional_parameters.items())
            # Filter out any None values
            # Accounting for mutually exclusive options
            for param in param_list:
                if param[0] != 'or' and param[1] is None:
                    logger.debug(f"Removing invalid option key '{param[0]}'")
                    optional_parameters.pop(param[0])
        extended_cli_func = self.process_options(
            optional_parameters, extended_cli_func_required)
        return extended_cli_func

# Imports
from __future__ import print_function
import getpass
import os
import re
import sys
from string import Template

from ansible_taskrunner.config import AppConfig
from bertdotconfig.configutils import AttrDict
from ansible_taskrunner.libs.cli.invocation import get_invocation
from ansible_taskrunner.libs.click_extras import ExtendCLI
from ansible_taskrunner.libs.click_extras.help import ExtendedHelp
from ansible_taskrunner.libs.proc_mgmt import CLIInvocation
from ansible_taskrunner.logger import Logger
from ansible_taskrunner.libs.cli.click_commands_create_group import CLICK_Commands_CLI_Group
from ansible_taskrunner.libs.cli.click_commands_create_init import CLICK_Commands_INIT
from ansible_taskrunner.libs.cli.click_commands_create_sub import CLICK_Commands_SUB
from ansible_taskrunner.libs.cli.click_commands_init_sub import CLICK_Commands_SUB_INIT

logger_obj = Logger()
logger = logger_obj.init_logger(__name__)

class CLI(CLICK_Commands_CLI_Group, CLICK_Commands_INIT, CLICK_Commands_SUB, CLICK_Commands_SUB_INIT):

  def __init__(self, **kwargs):

    script_name = kwargs['script_name']
    self.is_windows = kwargs.get('is_windows')
    self.doc = kwargs['doc']
    self.version = kwargs['version']
    self.exe_path = None
    self.cli_args = None
    self.cli_args_short = None
    self.local_username = None
    self.parameter_sets = None
    self.sys_platform = None
    self.cli_invocation = get_invocation(script_name)
    self.param_set = self.cli_invocation['param_set']
    # Parameter set var (if it has been specified)
    self.paramset_var = 'parameter_sets="%s"' % (
        ','.join(self.param_set) if self.param_set else 'False')
    self.raw_args = self.cli_invocation['raw_args']
    self.tasks_file = self.cli_invocation.get('tasks_file_override') or self.cli_invocation['tasks_file']
    self.tasks_file_override = self.cli_invocation['tasks_file_override']
    # Path to specified Taskfile
    self.tf_path = os.path.normpath(os.path.expanduser(self.tasks_file))
    # Instantiate the cli invocation class
    self.sub_process = CLIInvocation()
    self.special_vars_pattern = re.compile('ANSIBLE_EXTRA_VARS')
    self.skip_keys_pattern = re.compile('ANSIBLE_EXTRA_VARS')
    self.skip_values_pattern = re.compile('{{ .* }}')
    # Configuration Files
    self.attrdict = AttrDict()
    self.config_file = 'config.yaml'
    self.sftp_config_file = 'sftp-config.json'

    # Initialize Config Reader
    self.app_config = AppConfig()
    self.config = self.app_config.initialize()

    try:
        self.local_username = getpass.getuser()
    except Exception:
        self.local_username = os.environ.get('USERNAME') or os.environ.get('USER')

    self.help_max_content_width = self.config.get('help.max_content_width')
    self.logging_maxBytes = self.config.get('logging.maxBytes')
    self.logging_backupCount = self.config.get('logging.backupCount')
    self.debug = self.config.get('logging.debug')
    self.verbose = self.config.get('logging.verbose')
    self.suppress_output = self.config.get('logging.silent')
    self.log_file = self.config.get('logging.log_file')
    self.path_string = self.config.get('taskfile.path_string')

    if os.path.exists(self.tf_path):
        self.yaml_data = self.app_config.initialize(config_file=self.tf_path)
    else:
        logger.warning(
            "Couln't find %s or any other Tasks Manifest" % self.tf_path
        )
        self.yaml_data = {}

    # Extend CLI Options as per Tasks Manifest
    self.yaml_vars = self.yaml_data.get(self.path_string, {})

    # cli_args
    self._sys_args = [a for a in sys.argv if a != '--help']
    self.cli_args = ' '.join(self._sys_args)
    self.cli_args_short = ' '.join(self._sys_args[1:])

    # Populate list of available variables for use in internal string Templating
    self.available_vars = {}
    if self.yaml_vars:
        for k,v in self.yaml_vars.items():
            if isinstance(v, str):
                self.available_vars[k] = v
    self.available_vars['cli_args'] = self.cli_args
    self.available_vars['cli_args_short'] = self.cli_args_short
    self.available_vars['local_username'] = self.local_username
    self.available_vars['tf_path'] = self.tf_path
    self.available_vars = self.attrdict.merge(self.available_vars, os.environ)

    # Create a dictionary object holding option help messages
    self.option_help_messages = {}
    if os.path.exists(self.tf_path):
        string_pattern = re.compile('(.*-.*)##(.*)')
        for line in open(self.tf_path).readlines():
          match = string_pattern.match(line)
          if match:
            opt = match.groups()[0].strip().split(':')[0]
            oph = match.groups()[1].strip()
            self.option_help_messages[opt] = Template(oph).safe_substitute(**self.available_vars)

    # Instantiate the class for extending click options
    self.global_options = {}
    if self.yaml_vars:
        self.global_options = self.yaml_vars.get('globals.options', {})
    self.extend_cli = ExtendCLI(
        available_vars=self.available_vars,
        parameter_set=self.param_set,
        global_options=self.global_options,
        command_vars=self.yaml_vars,
        help_msg_map=self.option_help_messages)
    self.ExtendedHelp = ExtendedHelp

    # Detect command provider
    cli_provider = self.yaml_vars.get('cli_provider')
    if cli_provider == 'bash':
        from ansible_taskrunner.libs.providers import bash as bash_cli
        self.provider_cli = bash_cli.ProviderCLI()
    elif cli_provider == 'vagrant':
        from ansible_taskrunner.libs.providers import vagrant as vagrant_cli
        self.provider_cli = vagrant_cli.ProviderCLI()
    else:
        from ansible_taskrunner.libs.providers import ansible as ansible_cli
        self.provider_cli = ansible_cli.ProviderCLI()
    # Activate any plugins if found
    if os.path.isdir("plugins/providers"):
        import plugins
        # Activate Plugins if any are found
        plugin = plugins.Plugin(provider=cli_provider)
        plugins = plugin.activatePlugins()
        # CLI Provider Plugins
        for provider in plugins.providers:
            self.provider_cli = provider.ProviderCLI()


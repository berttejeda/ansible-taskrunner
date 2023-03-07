# -*- coding: utf-8 -*-

# Imports
import os
import sys

# Import third-party and custom modules
import ansible_taskrunner
from ansible_taskrunner.logger import Logger
from ansible_taskrunner.libs.cli import CLI
from getversion import get_module_version

# Account for script packaged as an exe via cx_freeze
if getattr(sys, 'frozen', False):
    # frozen
    self_file_name = script_name = os.path.basename(sys.executable)
else:
    # unfrozen
    self_file_name = os.path.basename(__file__)
    if self_file_name == '__main__.py':
        script_name = os.path.dirname(__file__)
    else:
        script_name = self_file_name

# OS Detection
is_windows = True if sys.platform in ['win32', 'cygwin'] else False

# set Windows console in VT mode
if is_windows:
    try:
        kernel32 = __import__("ctypes").windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        del kernel32
    except Exception:
        pass

# Cover My A$$
_cma = """
 CMA:
    This software is made available by the author in the hope
    that it will be useful, but without any warranty.
    The author is not liable for any consequence related to the
    use of the provided application.
"""

_doc = """\b
ansible-taskrunner - ansible-playbook wrapper
- YAML-abstracted python click cli options
- Utilizes a specially-formatted ansible-playbook (Taskfile.yaml)
  to extend the ansible playbook command via
  the python click module
"""

logger_obj = Logger()
logger = logger_obj.init_logger('cli')

# Private variables
__author__ = 'berttejeda'
__version__ = get_module_version(ansible_taskrunner)[0]
__program_name__ = 'tasks'

logger.debug(f'{__program_name__} version is {__version__}')

cli_obj = CLI(is_windows=is_windows, doc=_doc, script_name=script_name, version=__version__)
cli = cli_obj.create_cli_group()

if not cli_obj.cli_args_short == '--version':
    # Replace cli invocation in case we're calling the script directly
    # This allows for overriding the command manifest file, A.K.A. Taskfile.yaml
    if __name__ in ['ansible_taskrunner.cli', '__main__']:
        sys.argv = cli_obj.cli_invocation['cli']

    # Initialize the 'init' subcommand
    cli_obj.create_cli_init_command(cli)

    # Gather any subcommands defined in the command manifest
    cli_commands = cli_obj.yaml_vars.get('commands', {})

    # Initialize subcommands
    cli_obj.init_cli_sub_command(cli_obj, cli, commands=cli_commands)

if __name__ == '__main__':
    sys.exit(cli())

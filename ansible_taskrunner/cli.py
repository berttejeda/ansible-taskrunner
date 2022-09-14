# -*- coding: utf-8 -*-
# Import builtins
from __future__ import print_function
import getpass
import logging
import logging.handlers
import os
import re
import sys
from collections import OrderedDict
from getversion import get_module_version
from string import Template
import ansible_taskrunner

# OS Detection
is_windows = True if sys.platform in ['win32', 'cygwin'] else False
is_darwin = True if sys.platform in ['darwin'] else False

# Account for script packaged as an exe via cx_freeze
if getattr(sys, 'frozen', False):
    # frozen
    self_file_name = script_name = os.path.basename(sys.executable)
    project_root = os.path.dirname(os.path.abspath(sys.executable))
else:
    # unfrozen
    self_file_name = os.path.basename(__file__)
    if self_file_name == '__main__.py':
        script_name = os.path.dirname(__file__)
    else:
        script_name = self_file_name
    project_root = os.path.dirname(os.path.abspath(__file__))

# Modify our sys path to include the script's location
sys.path.insert(0, project_root)
# Make the zipapp work for python2/python3
py_path = 'py3' if sys.version_info[0] >= 3 else 'py2'
sys.path.insert(0, os.path.join(project_root, 'libs', py_path))

# set Windows console in VT mode
if is_windows:
    try:
        kernel32 = __import__("ctypes").windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        del kernel32 
    except Exception:
        pass

# Import third-party and custom modules
try:
    import click
    from libs.cliutil import get_invocation
    from libs.errorhandler import catchException
    from libs.errorhandler import ERR_ARGS_TASKF_OVERRIDE
    from libs.formatting import logging_format
    from libs.bastion_mode import init_bastion_settings
    from libs.help import SAMPLE_CONFIG
    from libs.help import SAMPLE_TASKS_MANIFEST
    from libs.help import SAMPLE_SFTP_CONFIG
    from libs.logger import init_logger
    from libs.superduperconfig import SuperDuperConfig
    from libs.click_extras import ExtendedEpilog
    from libs.click_extras import ExtendedHelp
    from libs.click_extras import ExtendCLI
    from libs.proc_mgmt import shell_invocation_mappings
    from libs.proc_mgmt import CLIInvocation
    from libs.yamlr import YamlReader
    # TODO
    # Employ language/regional options    
    # from libs.language import get_strings
except ImportError as e:
    print('Error in %s ' % os.path.basename(self_file_name))
    print('Failed to import at least one required module')
    print('Error was %s' % e)
    print('Please install/update the required modules:')
    print('pip install -U -r requirements.txt')
    sys.exit(1)

# Cover My A$$
_cma = """
 CMA:
    This software is made available by the author in the hope
    that it will be useful, but without any warranty.
    The author is not liable for any consequence related to the
    use of the provided application.
"""

_doc = """
Ansible Taskrunner - ansible-playbook wrapper
- YAML-abstracted python click cli options
- Utilizes a specially-formatted ansible-playbook (Taskfile.yaml)
  to extend the ansible playbook command via
  the python click module
"""

# Private variables
__author__ = 'etejeda'
# Version
__version__ = get_module_version(ansible_taskrunner)[0]

__program_name__ = 'tasks'

# Logging
logger = init_logger()

# We'll pass this down to the run invocation
global exe_path
global cli_args
global cli_args_short
global local_username
global parameter_sets
global sys_platform
global tf_path

cli_invocation = get_invocation(script_name)

try:
    local_username = getpass.getuser() 
except Exception:
    local_username = os.environ.get('USERNAME') or os.environ.get('USER')

param_set = cli_invocation['param_set']
raw_args = cli_invocation['raw_args']
tasks_file = cli_invocation.get('tasks_file_override') or cli_invocation['tasks_file']
tasks_file_override = cli_invocation['tasks_file_override']

# Replace the commandline invocation
if __name__ in ['ansible_taskrunner.cli', '__main__']:
    sys.argv = cli_invocation['cli']

# System Platform
sys_platform = sys.platform
exe_path = os.path.normpath(self_file_name)
exe_path = re.sub('.__main__.py','', exe_path)

# Parameter set var (if it has been specified)
paramset_var = 'parameter_sets="%s"' % (
    ','.join(param_set) if param_set else 'False')
parameter_sets = paramset_var

# Path to specified Taskfile
tf_path = os.path.normpath(os.path.expanduser(tasks_file))

# Instantiate YAML Reader Class
yamlr = YamlReader()
# Instantiate the cli invocation class
sub_process = CLIInvocation()
# Load Tasks Manifest
yaml_input_file = tasks_file

# Initialize Config Module
superconf = SuperDuperConfig(__program_name__)

# Configuration Files
config_file = 'config.yaml'
sftp_config_file = 'sftp-config.json' 
config = superconf.load_config(config_file)
help_max_content_width = yamlr.deep_get(config, 'help.max_content_width', 200)
logging_maxBytes = yamlr.deep_get(config, 'logging.maxBytes', 10000000)
logging_backupCount = yamlr.deep_get(config, 'logging.backupCount', 5)
__debug = yamlr.deep_get(config, 'logging.debug', False)
verbose = yamlr.deep_get(config, 'logging.verbose', 0)
suppress_output = yamlr.deep_get(config, 'logging.silent', 0)
log_file = yamlr.deep_get(config, 'logging.log_file', None)
path_string = yamlr.deep_get(config, 'taskfile.path_string', 'vars')

if os.path.exists(yaml_input_file):
    yaml_data = superconf.load_config(yaml_input_file, data_key=0)
else:
    logger.warning(
        "Couln't find %s or any other Tasks Manifest" % yaml_input_file
    )
    yaml_data = {}
# Extend CLI Options as per Tasks Manifest
yaml_vars = yamlr.get(yaml_data, path_string)    

# cli_args
_sys_args = [a for a in sys.argv if a != '--help']
cli_args = ' '.join(_sys_args)
cli_args_short = ' '.join(_sys_args[1:])

# Populate list of available variables for use in internal string Templating
available_vars = dict([(v, globals()[v]) for v in globals().keys() if not v.startswith('_')])

# Create a dictionary object holding option help messages
option_help_messages = {}
if os.path.exists(tf_path):
    string_pattern = re.compile('(.*-.*)##(.*)')
    for line in open(tf_path).readlines():
      match = string_pattern.match(line)
      if match:
        opt = match.groups()[0].strip().split(':')[0]
        oph = match.groups()[1].strip()
        option_help_messages[opt] = Template(oph).safe_substitute(**available_vars)
# Instantiate the class for extending click options
extend_cli = ExtendCLI(vars_input=yaml_vars, parameter_set=param_set, help_msg_map=option_help_messages)

# Detect command provider
global provider_cli
cli_provider = yamlr.deep_get(config, 'cli.providers.default', {})
cli_provider = yaml_vars.get('cli_provider', cli_provider)
if cli_provider == 'bash':
    from libs.providers import bash as bash_cli
    provider_cli = bash_cli.ProviderCLI()
elif cli_provider == 'vagrant':
    from libs.providers import vagrant as vagrant_cli
    provider_cli = vagrant_cli.ProviderCLI()
else:
    from libs.providers import ansible as ansible_cli
    provider_cli = ansible_cli.ProviderCLI()
# Activate any plugins if found
if os.path.isdir("plugins/providers"):
    import plugins
    global plugins
    # Activate Plugins if any are found
    plugin = plugins.Plugin(provider=cli_provider)
    plugins = plugin.activatePlugins()
    # CLI Provider Plugins
    for provider in plugins.providers:
        provider_cli = provider.ProviderCLI()
# Main CLI interface
click_help = """\b
Ansible Taskrunner - ansible-playbook wrapper
- YAML-abstracted python click cli options
- Utilizes a specially-formatted ansible-playbook (Taskfile.yaml)
  to extend the ansible playbook command via
  the python click module
    """
click_help_epilog = ""

@click.group(cls=ExtendedEpilog, help=click_help, epilog=click_help_epilog, context_settings=dict(max_content_width=help_max_content_width))
@click.version_option(version=__version__)
@click.option('--config', type=str, nargs=1,
              help='Specify a config file (default is config.ini)')
@click.option('--debug', is_flag=True, help='Enable debug output')
@click.option('--silent', is_flag=True, help='Suppress all output')
@click.option('--verbose', count=True,
              help='Increase verbosity of output')
@click.option('--log', is_flag=True, help='Enable output logging')
def cli(**kwargs):
    global config, config_file, __debug, verbose, loglevel, logger, suppress_output
    suppress_output = True if kwargs.get('silent') else False
    # Are we specifying an alternate config file?
    if kwargs['config']:
        config = superconf.load_config(config_file)
    if config is None:
        logger.debug('No valid config file found %s' % config_file)
        logger.debug('Using program defaults')
        # Verbose mode enabled?
    verbose = kwargs.get('verbose', None)
    # Debug mode enabled?
    __debug = kwargs.get('debug', None)
    # Set up logging with our desired output level
    if __debug:
        loglevel = logging.DEBUG  # 10
    elif verbose:
        loglevel = logging.INFO  # 20
    else:
        loglevel = logging.INFO  # 20
    logger.setLevel(loglevel)
    if suppress_output:
        if sys.version_info[0] >= 3:
            logging.disable(sys.maxsize) # Python 3        
        else:
            logging.disable(sys.maxint) # Python 2
    # Add the log  file handler to the logger, if applicable
    if kwargs.get('log') and not log_file:
        logger.warning('Logging enabled, but no log_file specified in %s' % config_file)
    if kwargs.get('log') and log_file:
        filehandler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=logging_maxBytes, backupCount=logging_backupCount)
        formatter = logging.Formatter(logging_format)
        filehandler.setFormatter(formatter)
        logger.addHandler(filehandler)
    logger.debug('Debug Mode Enabled, keeping any generated temp files')
    return

init_epilog = ''
if is_windows:
    init_epilog = '''
Examples:
- Initialize an empty workspace
    tasks init
- Initialize an empty workspace config with username and remote path
    tasks init -h myhost.example.org -u {0} -r "/home/{0}/git/ansible"
'''.format(local_username)

# Init command
@cli.command(cls=ExtendedHelp, help='Initialize local directory with sample files',
    epilog=init_epilog, context_settings=dict(max_content_width=180))
@click.version_option(version=__version__)
@click.option('---show-samples', is_flag=True,
              help='Only show a sample task manifest, don\'t write it')
@extend_cli.bastion_mode
def init(**kwargs):
    logger.info('Initializing ...')
    if kwargs.get('_show_samples'):
        logger.info('Displaying sample config')
        print(SAMPLE_CONFIG)
        logger.info('Displaying sample manifest')
        print(SAMPLE_TASKS_MANIFEST)
        if is_windows:
            logger.info('Displaying sample sftp config')
            print(SAMPLE_SFTP_CONFIG)            
    else:
        if not os.path.exists(config_file):
            logger.info(
                'Existing config not found, writing %s' % config_file)
            with open(config_file, 'w') as f:
                f.write(SAMPLE_CONFIG)
        else:
            logger.info(
                'File exists, not writing sample config %s' % config_file)
        if not os.path.exists(tasks_file):
            logger.info(
                'Existing manifest not found, writing %s' % tasks_file)
            with open(tasks_file, 'w') as f:
                f.write(SAMPLE_TASKS_MANIFEST)
        else:
            logger.info(
                'File exists, not writing manifest %s' % tasks_file)
        if is_windows or kwargs.get('_bastion_mode'):
            settings_vars = init_bastion_settings(kwargs)
            if not os.path.exists(sftp_config_file):
                logger.info(
                    'Existing sftp config not found, writing %s' % sftp_config_file)
                with open(sftp_config_file, 'w') as f:
                    f.write(Template(SAMPLE_SFTP_CONFIG).safe_substitute(**settings_vars))
            else:
                logger.info(
                    'File exists, not writing sftp config %s' % sftp_config_file)

# Run command
# Parse help documentation
help_string = yamlr.deep_get(yaml_vars, 'help.message', 'Run the specified Taskfile')
help_string = Template(help_string).safe_substitute(**available_vars)
epilog_string = yamlr.deep_get(yaml_vars, 'help.epilog', '')
examples = yamlr.deep_get(yaml_vars, 'help.examples', '')
examples_string = ''
# Treat the make-mode internal bash functions
function_help_string = ''    
# Bash functions
bash_functions = []    
yaml_vars_functions = yaml_vars.get('functions', {})
internal_functions = {}
if yaml_vars_functions:
    internal_functions = yaml_vars_functions
    # Append the special make_mode_engage bash function
    internal_functions['make_mode_engage'] = {
'help': 'Engage Make Mode',
'shell': 'bash',
'hidden': 'true',
'source': '''
    echo Make Mode Engaged
    echo Invoking ${1} function
    ${1}
                '''
    }    
    for f in internal_functions:
        f_shell = yamlr.deep_get(yaml_vars, 'functions.%s.shell' % f, {})
        source = yamlr.deep_get(yaml_vars, 'functions.%s.source' % f, {})
        if f_shell and source:
            function_source = shell_invocation_mappings[f_shell].format(src=source)
            bash_functions.append(
                'function {fn}(){{\n{fs}\n}}'.format(
                    fn=f, fs=function_source)
            )
for f in internal_functions:
    if yamlr.deep_get(internal_functions, '%s.hidden' % f, {}) or \
    not yamlr.deep_get(internal_functions, '%s.help' % f, {}):
        continue
    f_help_string = internal_functions[f].get('help')
    function_help_string += '{fn}: {hs}\n'.format(fn=f, hs=f_help_string)        
if isinstance(examples, list):
    for example in examples:
        if isinstance(example, dict):
            for key, value in example.items():
                value = Template(value).safe_substitute(**available_vars)
                examples_string += '- {k}:\n{v}'.format(k=key, v=value)
        if isinstance(example, str):
            example = Template(example).safe_substitute(**available_vars)
            examples_string += '%s\n' % example
epilog = '''
{ep}
Examples:

{ex}

Available make-style functions:

{fh}
    '''.format(ep=epilog_string, 
        ex=examples_string or 'None', 
        fh=function_help_string or 'None')
epilog = Template(epilog).safe_substitute(**available_vars)
@cli.command(cls=ExtendedHelp, help="{h}".format(h=help_string),
             epilog=epilog)
@click.version_option(version=__version__)
@click.option('---make', 'make_mode_engage', is_flag=False,
              help='Call make-style function',
              required=False)
@click.option('---echo',
              is_flag=True,
              help='Don\'t run, simply echo underlying commands')
@extend_cli.options
@extend_cli.bastion_mode
@provider_cli.options
def run(args=None, **kwargs):
    global param_set
    # Process Raw Args
    # Process run args, if any
    args = ' '.join(args) if args else ''
    # Silence Output if so required
    # Initialize values for subshell
    prefix = 'echo' if kwargs.get('_echo') else ''
    # Are we executing commands via bastion host?
    bastion_settings = {}
    # Force bastion mode if running from a Windows host
    bastion_mode_enabled = True if is_windows else kwargs.get('_bastion_mode', False)
    if bastion_mode_enabled:
        bastion_settings = {
        'config_file': yamlr.deep_get(config, 'bastion_mode.config_file', 'sftp-config.json'),
        # Turn bastion Mode off if we explicitly don't want it
        'enabled': yamlr.deep_get(config, 'bastion_mode.enabled', True),
        'keep_alive': yamlr.deep_get(config, 'bastion_mode.keep_alive', True),
        'poll_wait_time': yamlr.deep_get(config, 'bastion_mode.poll_wait_time', 5),
        'sftp_sync': yamlr.deep_get(config, 'bastion_mode.sync', True)
        }
    # Gather variables from commandline for interpolation
    cli_vars = ''
    # python 2.x
    # Make sure kwargs adhere to the order in 
    # which they were called
    if sys.version_info[0] < 3:
        # First we build a mapping of cli variables to corresponding yaml variables
        parameter_mapping = {}
        req_parameters = yaml_vars.get('required_parameters', {}) or {}
        opt_parameters = yaml_vars.get('optional_parameters', {}) or {}
        # We need to 'inject' built-in cli options
        # since we're artificially re-ordering things
        ctx = click.get_current_context()
        # Parse the help message to extract cli options
        ctx_help = ctx.get_help()
        existing_provider_options = re.findall('---.*?[\s]', ctx_help)
        for opt in existing_provider_options:
            opt = opt.strip()
            opt_parameters[opt] = opt.replace('---', '_').replace('-', '_')
        # We're working with the optional 
        # parameter set in either case
        if req_parameters:
            d_req = dict(req_parameters)
            d_opt = dict(opt_parameters)
            d_req.update(d_opt)
            parameter_mapping = d_req
        else:
            parameter_mapping = dict(opt_parameters)
        # Next, we create a dictionary that holds cli arguments 
        # in the order they were called, as per the parameter mapping
        ordered_args = {}
        for k, v in parameter_mapping.items():
            for a in sys.argv:
                try:
                    if re.match(k, a):
                        for o in k.split('|'):
                            if o in sys.argv:
                                i = sys.argv.index(o)
                                ordered_args[k] = i
                except Exception as e:
                    logger.debug("Skipped {_k} due to error {_e}".format(_k=k, _e=e))
        # Lastly, we convert our kwargs object to
        # an ordered dictionary object as per the above
        # making sure we include any existing kwargs items
        ordered_args_tuples = []
        for k, v in sorted(ordered_args.items(), key=lambda item: item[1]):
            if isinstance(parameter_mapping[k], str):
                o_tuple = (parameter_mapping[k], kwargs.get(parameter_mapping[k]))
                kwargs.pop(parameter_mapping[k], None)
            else:
                logger.error('Unexpected parameter mapping "%s", check your cli invocation' % k)
                sys.exit(1)
            ordered_args_tuples.append(o_tuple)
        new_kwargs = ordered_args_tuples + [(k,v) for k,v in kwargs.items()]
        kwargs = OrderedDict(new_kwargs)
    # cli-provided variables
    # List-type variables
    list_vars = []    
    for key, value in kwargs.items():
        if key.startswith('_'):
            cli_vars += '{k}="{v}"\n'.format(k=key, v=value)
        elif value and key not in internal_functions.keys():
            if isinstance(value, list) or isinstance(value, tuple):
                list_vars.append('{k}=$(cat <<EOF\n{v}\nEOF\n)'.format(
                    k=key, v='\n'.join(value)))
            else:
                cli_vars += '{k}="{v}"\n'.format(k=key, v=value)
    # Gather default variables
    vars_list = []
    kwargs_list = [(k,v) for k,v in kwargs.items() if v]
    kwargs_dict_filtered = dict([(k,v) for k,v in kwargs.items() if v])
    # Define the list of yaml variables, excluding the 'inventory' variable (if applicable)
    yaml_variables = [(key,value) for key,value in yaml_vars.items() if not isinstance(value, dict) and not key == 'inventory']
    # Define the list of default variables, 
    # ensuring we only keep those that were 
    # not overridden via cli option
    for var in yaml_variables:
        if var[0] not in [d[0] for d in kwargs_list]:
            vars_list.append((var[0],var[1]))
        else:
            vars_list.append((var[0], kwargs_dict_filtered[var[0]]))
    if sys.version_info[0] < 3:
        default_vars = OrderedDict(vars_list)
    else:
        default_vars = dict(vars_list)
    for var in default_vars:
        if isinstance(default_vars[var], list):
            _var = default_vars[var]
            try:
                list_vars.append('{k}=$(cat <<EOF\n{v}\nEOF\n)'.format(
                    k=var, v='\n'.join(_var)))
            except TypeError as e:
                logger.debug("Unsupported variable type, skipped variable '%s'" % var)
                logger.debug("Skip Reason %s" % e)
    # String-type variables
    defaults_string_vars = [] 
    for var in default_vars:
        if isinstance(default_vars[var], str):
            try:
                _var = default_vars[var]
                defaults_string_vars.append(
                    '{k}="""{v}"""'.format(k=var, v=_var))
            except TypeError as e:
                logger.debug("Unsupported variable type, skipped variable '%s'" % var)
                logger.debug("Skip Reason %s" % e)
    # Append the __tasks_file variable to the above list
    defaults_string_vars.append(
        '__tasks_file__=%s' % tf_path
        )
    inventory_variable = 'inventory="""{v}"""'.format(v=yamlr.deep_get(yaml_vars, 'inventory', ''))
    defaults_string_vars.append(inventory_variable)
    # Short-circuit the task runner
    # if we're calling functions from the commandline
    cli_functions = ['{k} {v}'.format(
        k=key, v='' if value in [True, False] else value) for key, value in kwargs.items() if
                     value and key in internal_functions.keys()]
    if cli_functions:
        command = '''{clv}
{dsv}
{psv}
{dlv}
{bfn}
{clf} {arg} {raw}
            '''.format(
                dsv='\n'.join(defaults_string_vars),
                psv=paramset_var,
                dlv='\n'.join(list_vars),
                clv=cli_vars,
                bfn='\n'.join(bash_functions),
                clf='\n'.join(cli_functions),
                arg=args,
                raw=raw_args
            )
        if prefix == 'echo':
            print(command)
        else:
            sub_process.call(command, debug_enabled=__debug, suppress_output=suppress_output)
    else:
        # Invoke the cli provider
        provider_cli.invocation(
            args=args,
            bash_functions=bash_functions,
            bastion_settings=bastion_settings,
            cli_vars=cli_vars,
            debug=__debug,
            default_vars=default_vars,
            invocation=cli_invocation,
            kwargs=kwargs,
            paramset_var=paramset_var,
            prefix=prefix,
            raw_args=raw_args,
            string_vars=defaults_string_vars,
            suppress_output=suppress_output,
            yaml_input_file=yaml_input_file,
            yaml_vars=yaml_vars
        )

if __name__ == '__main__':
    sys.exit(cli())

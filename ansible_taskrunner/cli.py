# -*- coding: utf-8 -*-
# Import builtins
from __future__ import print_function
from collections import OrderedDict
import logging
import logging.handlers
import os
import re
import sys
from string import Template

# For zip-app
self_file_name = os.path.basename(__file__)
if self_file_name == '__main__.py':
    script_name = os.path.dirname(__file__)
else:
    script_name = self_file_name

# Needed for zip-app
# Make the zipapp work for python2/python3
py_path = 'py3' if sys.version_info[0] >= 3 else 'py2'
project_root = os.path.dirname(os.path.abspath(__file__))
is_windows = True if sys.platform in ['win32', 'cygwin'] else False
is_darwin = True if sys.platform in ['darwin'] else False
if is_windows:
    sys.path.insert(0, project_root + '\\lib')
    sys.path.insert(0, project_root + '\\lib\\%s' % py_path)
elif is_darwin:
    sys.path.insert(0, project_root + '/lib')
    sys.path.insert(0, project_root + '/lib/%s' % py_path)
else:
    sys.path.insert(0, project_root + '/lib')
    sys.path.insert(0, project_root + '/lib/%s' % py_path)

# Import third-party and custom modules
try:
    import click
    from cliutil import get_invocation
    from errorhandler import catchException
    from errorhandler import ERR_ARGS_TASKF_OVERRIDE
    from formatting import logging_format
    from help import SAMPLE_CONFIG
    from help import SAMPLE_TASKS_MANIFEST
    if is_windows:
        from help import SAMPLE_SFTP_CONFIG    
    from logger import init_logger
    from superduperconfig import SuperDuperConfig
    from click_extras import ExtendedEpilog
    from click_extras import ExtendedHelp
    from click_extras import ExtendCLI
    from proc_mgmt import shell_invocation_mappings
    from proc_mgmt import CLIInvocation
    from yamlr import YamlReader
    # TODO
    # Employ language/regional options    
    # from lib.language import get_strings
except ImportError as e:
    print('Error in %s ' % os.path.basename(__file__))
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
- Utilizes a specially-formatted ansible-playbook
"""

# Private variables
__author__ = 'etejeda'
__version__ = '1.1.10'
__program_name__ = 'tasks'
__debug = False
verbose = 0
log_file = None

# Logging
logger = init_logger()

# Load Config(s)
config_file = 'config.yaml'
sftp_config_file = 'sftp-config.json' 
superconf = SuperDuperConfig(__program_name__)
config = superconf.load_config(config_file)

# We'll pass this down to the run invocation
global exe_path
global cli_args
global cli_args_short
global parameter_sets
global sys_platform
global tf_path

invocation = get_invocation(script_name)

path_string='vars'
param_set = invocation['param_set']
tasks_file = invocation['tasks_file']

# Replace the commandline invocation
if __name__ in ['ansible_taskrunner.cli', '__main__']:
    sys.argv = invocation['cli']

# System Platform
sys_platform = sys.platform
exe_path = os.path.normpath(__file__)
exe_path = re.sub('.__main__.py','', exe_path)

# Parameter set var (if it has been specified)
parameter_sets = ' '.join(param_set)
paramset_var = 'parameter_sets="%s"' % (
    ' '.join(param_set) if param_set else 'False')

# Path to specified Taskfile
tf_path = os.path.normpath(os.path.expanduser(tasks_file))

# Instantiate YAML Reader Class
yamlr = YamlReader()
# Instantiate the cli invocation class
sub_process = CLIInvocation()
# Load Tasks Manifest
yaml_input_file = tasks_file
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
    from providers import bash as bash_cli
    provider_cli = bash_cli.ProviderCLI()
elif cli_provider == 'vagrant':
    from providers import vagrant as vagrant_cli
    provider_cli = vagrant_cli.ProviderCLI()
else:
    from providers import ansible as ansible_cli
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
- Utilizes a specially-formatted ansible-playbook
  to extend the ansible playbook command via
  the python click module
    """
click_help_epilog = ""

@click.group(cls=ExtendedEpilog, help=click_help, epilog=click_help_epilog, context_settings=dict(max_content_width=120))
@click.version_option(version=__version__)
@click.option('--config', '-C', type=str, nargs=1,
              help='Specify a config file (default is config.ini)')
@click.option('--debug', '-d', is_flag=True, help='Enable debug output')
@click.option('--verbose', '-v', count=True,
              help='Increase verbosity of output')
@click.option('--log', '-l', type=str,
              help='Specify (an) optional log file(s)')
def cli(**kwargs):
    global config, config_file, __debug, verbose, loglevel, logger
    # Are we specifying an alternate config file?
    if kwargs['config']:
        config = superconf.load_config(config_file)
    if config is None:
        logger.warning('No valid config file found %s' % config_file)
        logger.warning('Using program defaults')
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
    # Add the log  file handler to the logger, if applicable
    logfilename = kwargs.get('log')
    if logfilename:
        filehandler = logging.handlers.RotatingFileHandler(
            logfilename, maxBytes=10000000, backupCount=5)
        formatter = logging.Formatter(logging_format)
        filehandler.setFormatter(formatter)
        logger.addHandler(filehandler)
    logger.debug('Debug Mode Enabled, keeping any generated temp files')
    return 0

# Init command
@cli.command(help='Initialize local directory with sample files')
@click.version_option(version=__version__)
@click.option('--show-samples', '-m', is_flag=True,
              help='Only show a sample task manifest, don\'t write it')
def init(**kwargs):
    logger.info('Initializing ...')
    if kwargs['show_samples']:
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
        if not os.path.exists(sftp_config_file):
            logger.info(
                'Existing manifest not found, writing %s' % sftp_config_file)
            with open(sftp_config_file, 'w') as f:
                f.write(SAMPLE_SFTP_CONFIG)
        else:
            logger.info(
                'File exists, not writing manifest %s' % sftp_config_file)

# Run command
# Parse help documentation
help_string = yamlr.deep_get(yaml_vars, 'help.message', '')
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
        ex=examples_string, 
        fh=function_help_string)
epilog = Template(epilog).safe_substitute(**available_vars)
@cli.command(cls=ExtendedHelp, help="{h}".format(h=help_string),
             epilog=epilog)
@click.version_option(version=__version__)
@click.option('---make', 'make_mode_engage', is_flag=False,
              help='Call make-style function',
              required=False)
@click.option('---raw', is_flag=False,
              help='Specify raw options for underlying subprocess',
              required=False)
@click.option('---bastion-mode',
              is_flag=True,
              help='Execute commands via a bastion host')
@click.option('---echo',
              is_flag=True,
              help='Don\'t run, simply echo underlying commands')
@extend_cli.options
@provider_cli.options
def run(args=None, **kwargs):
    global param_set
    # Process Raw Args
    raw_args = kwargs['_raw'] if kwargs.get('_raw') else ''
    # Process run args, if any
    args = ' '.join(args) if args else ''
    # Initialize values for subshell
    prefix = 'echo' if kwargs.get('_echo') else ''
    # Are we executing commands via bastion host?
    bastion_settings = {}
    # Force bastion mode if running from a Windows host
    bastion_mode_enabled = True if is_windows else kwargs.get('_bastion_mode', False)
    if bastion_mode_enabled:
        # Turn bastion Mode off if we specifically don't want it
        if not os.environ.get('WIN32_NO_BASTION_MODE'):
            bastion_settings = {
            'enabled': True,
            'config_file': 'sftp-config.json',
            'poll_wait_time': 5,
            'keep_alive': True
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
                if re.match(k, a):
                    for o in k.split('|'):
                        if o in sys.argv:
                            i = sys.argv.index(o)
                            ordered_args[k] = i
        # Lastly, we convert our kwargs object to
        # an ordered dictionary object as per the above
        ordered_args_tuples = []
        for k, v in sorted(ordered_args.items(), key=lambda item: item[1]):
            o_tuple = (parameter_mapping[k], kwargs.get(parameter_mapping[k]))
            ordered_args_tuples.append(o_tuple)
        kwargs = OrderedDict(ordered_args_tuples)
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
    # List-type variables
    list_vars = []
    for var in default_vars:
        if isinstance(default_vars[var], list):
            _var = default_vars[var]
            try:
                list_vars.append('{k}=$(cat <<EOF\n{v}\nEOF\n)'.format(
                    k=var, v='\n'.join(_var)))
            except TypeError as e:
                logger.warning("Unsupported variable type, skipped variable '%s'" % var)
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
                logger.warning("Unsupported variable type, skipped variable '%s'" % var)
                logger.debug("Skip Reason %s" % e)
    # Append the __tasks_file variable to the above list
    defaults_string_vars.append(
        '__tasks_file__=%s' % tf_path
        )
    inventory_variable = 'inventory="""{v}"""'.format(v=yaml_vars['inventory'])
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
            sub_process.call(command, debug_enabled=__debug)
    else:
        # Invoke the cli provider
        provider_cli.invocation(
            yaml_input_file=yaml_input_file,
            yaml_vars=yaml_vars,
            bash_functions=bash_functions,
            cli_vars=cli_vars,
            paramset_var=paramset_var,
            default_vars=default_vars,
            string_vars=defaults_string_vars,
            prefix=prefix,
            debug=__debug,
            args=args,
            raw_args=raw_args,
            bastion_settings=bastion_settings,
            kwargs=kwargs
        )

if __name__ == '__main__':
    sys.exit(cli())

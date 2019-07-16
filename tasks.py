#!/usr/bin/env python
# coding=utf-8
""" Ansible Task Runner
"""

# Import builtins
from __future__ import print_function
from datetime import datetime
import logging
import logging.handlers
import os
import sys

# Import third-party and custom modules
try:
    if sys.version_info[0] >= 3:
        from lib.py3 import click
        from lib.py3 import yaml
    else:
        from lib.py2 import click
        from lib.py2 import yaml        
    from lib.common.errorhandler import catchException
    from lib.common.errorhandler import ERR_ARGS_TASKF_OVERRIDE
    from lib.common.formatting import reindent
    from lib.common.help import SAMPLE_CONFIG
    from lib.common.help import SAMPLE_TASKS_MANIFEST
    from lib.common.superduperconfig import SuperDuperConfig
    from lib.common.click_extras import ExtendedEpilog
    from lib.common.click_extras import ExtendedHelp
    from lib.common.click_extras import ExtendCLI
    from lib.common.yamlc import YamlCLIInvocation
    from lib.common.yamlr import YamlReader
except ImportError as e:
    print('Failed to import at least one required module')
    print('Error was %s' % e)
    print('Please install/update the required modules:')
    print('pip install -U -r requirements.txt')
    sys.exit(1)

# Private variables
__author__ = 'etejeda'
__version__ = '0.0.11-alpha'
__program_name__ = 'tasks'
__debug = False
verbose = 0
log_file = None

# Logging
# Set format
# Set up a specific logger with our desired output level and stdout formatter
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
streamhandler = logging.StreamHandler()
streamhandler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s"))
logger.addHandler(streamhandler)

# Load Config(s)
config_file = 'config.yaml'
superconf = SuperDuperConfig(__program_name__)
config = superconf.load_config(config_file)

# For zip-app
script_name = os.path.basename(__file__)
if script_name == '__main__.py':
    script_name = os.path.dirname(__file__)

def main(args, tasks_file='Taskfile.yaml', param_set=None, path_string='vars', cli_provider='default', debug=False):
    
    # We'll pass this down to the run invocation
    global _param_set
    _param_set = param_set

    # Instantiate YAML Reader Class
    yamlr = YamlReader()

    global provider_cli
    # Detect command provider
    cli_provider = yamlr.deep_get(config, 'cli.providers.default', {})
    if cli_provider == 'bash':
        from lib.common.providers import default as default_cli
        provider_cli = default_cli.ProviderCLI()
    elif cli_provider == 'vagrant':
        from lib.common.providers import vagrant as vagrant_cli
        provider_cli = vagrant_cli.ProviderCLI()
    else:
        from lib.common.providers import ansible as ansible_cli
        provider_cli = ansible_cli.ProviderCLI()
    
    # Load Tasks Manifest
    yaml_input_file = tasks_file
    yaml_path_string = path_string
    if os.path.exists(yaml_input_file):
        yaml_data = superconf.load_config(yaml_input_file, data_key=0)
    else:
        logger.warning("Couln't find %s or any other Tasks Manifest" % yaml_input_file)
        yaml_data = {}

    # Extend CLI Options as per Tasks Manifest
    yaml_vars = yamlr.get(yaml_data, yaml_path_string)
    extend_cli = ExtendCLI(vars_input=yaml_vars, parameter_set=param_set)

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

    HELP = """\b
    Task runner that serves as a higher-level automation layer to ansible
    The script expects a specially formatted ansible-playbook in order to function properly
    """
    EPILOG = ""

    @click.group(cls=ExtendedEpilog, help=HELP, epilog=EPILOG)
    @click.version_option(version=__version__)
    @click.option('--config', '-C', type=str, nargs=1, help='Specify a config file (default is config.ini)')
    @click.option('--debug', '-d', is_flag=True, help='Enable debug output')
    @click.option('--verbose', '-v', count=True, help='Increase verbosity of output')
    @click.option('--log', '-l', type=str, help='Specify (an) optional log file(s)')
    def cli(**kwargs):       
        global config, config_file, __debug, verbose, loglevel, logger
        # Are we specifying an alternate config file?
        if kwargs['config']:
            config = superconf.load_config(config_file)
        if config is None:
            logger.warning('No valid config file found %s, using program defaults' % config_file)        
        # Verbose mode enabled?
        verbose = kwargs['verbose']
        # Debug mode enabled?
        __debug = kwargs['debug']
        # Set up logging with our desired output level
        if __debug:
            loglevel = logging.DEBUG  # 10
        elif verbose:
            loglevel = logging.INFO  # 20
        else:
            loglevel = logging.INFO  # 20
        logger.setLevel(loglevel)
        # Add the log  file handler to the logger, if applicable
        logfilename = kwargs['log']
        if logfilename:
            filehandler = logging.handlers.RotatingFileHandler(logfilename, maxBytes=10000000, backupCount=5)
            formatter = logging.Formatter(
                "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
            filehandler.setFormatter(formatter)
            logger.addHandler(filehandler)
        logger.debug('Debug Mode Enabled, keeping any generated temp files')
        return 0

    # Examples command
    @cli.command(help="Initialize local directory with sample files to get your started")
    @click.version_option(version=__version__)
    @click.option('--show-samples', '-m', is_flag=True, help='Only show a sample task manifest, don\'t write it')
    def init(args=None, **kwargs):
        logger.info('Initializing ...')
        if kwargs['show_samples']:
            logger.info('Displaying sample config')
            print(SAMPLE_CONFIG)
            logger.info('Displaying sample manifest')
            print(SAMPLE_TASKS_MANIFEST)
        else:
            if not os.path.exists(config_file):
                logger.info('File does not exist ... writing sample config %s' % config_file)
                with open(config_file, 'w') as f:
                    f.write(SAMPLE_CONFIG)
            else:
                logger.info('File exists ... not writing sample config %s' % config_file)
            if not os.path.exists(tasks_file):
                logger.info('File does not exist ... writing sample manifest %s' % tasks_file)
                with open(tasks_file, 'w') as f:
                    f.write(SAMPLE_TASKS_MANIFEST)
            else:
                logger.info('File exists ... not writing sample manifest %s' % tasks_file)

    # Parse help documentation
    help_string = yamlr.deep_get(yaml_vars, 'help.message', '')
    epilog_string = yamlr.deep_get(yaml_vars, 'help.epilog', '')
    examples = yamlr.deep_get(yaml_vars, 'help.examples', '')
    examples_string = ''
    if isinstance(examples, list):
        for example in examples:
            if isinstance(example, dict):
                for key,value in example.items():
                    examples_string += '- {k}:\n{v}'.format(k=key, v=value)          
            if isinstance(example, str):
                examples_string += '%s\n' % example
    epilog = '''
    {ep}
    Examples:
    {ex}
    '''.format(ep=epilog_string, ex=examples_string)
    epilog = reindent(epilog, 0)
    
    # Run command
    @cli.command(cls=ExtendedHelp, help="{h}".format(h=help_string),
                 epilog=epilog)
    @click.version_option(version=__version__)
    @click.option('---raw', '---r', is_flag=False, help='Specify raw options to pass down to the underlying subprocess', required=False)
    @click.option('--echo',
                  is_flag=True,
                  help='Don\'t run, simply echo underlying commands')
    @extend_cli.options
    @provider_cli.options
    def run(args=None, **kwargs):
        # Process Raw Args
        raw_args = kwargs.get('_raw', '')
        # Instantiate the cli invocation class
        yamlcli = YamlCLIInvocation()
        args = ' '.join(args) if args else ''
        # Initialize values for subshell
        prefix = 'echo' if kwargs.get('echo') else ''
        # Default variables
        default_vars = dict([(key, value) for key, value in yaml_vars.items() if not isinstance(value, dict)])        
        # Parameter set var (if it has been specified)
        paramset_var = "parameter_set=%s" % (_param_set if _param_set else 'False')        
        # List-type variables
        list_vars = []
        for var in default_vars:
            if isinstance(default_vars[var], list):
                list_vars.append('{k}=$(cat <<EOF\n{v}\nEOF\n)'.format(k=var, v='\n'.join(default_vars[var])))
        # String-type variables
        defaults_string_vars = []
        for var in default_vars:
            if isinstance(default_vars[var], str):
                defaults_string_vars.append('{k}="""{v}"""'.format(k=var, v=default_vars[var]))                
        # Bash functions
        bash_functions = []
        functions = yaml_vars.get('functions', {})
        for f in functions:
            if yaml_vars['functions'][f].get('shell') and yaml_vars['functions'][f].get('source'):
                if yaml_vars['functions'][f]['shell'] == 'bash':
                    bash_functions.append('function {fn}(){{\n{fs}\n}}'.format(fn=f, fs=yaml_vars['functions'][f]['source']))        
        # Gather variables from commandline for interpolation
        cli_vars = ''
        for key, value in kwargs.items():
            if value and key not in functions.keys():
                if isinstance(value, list) or isinstance(value, tuple):
                    list_vars.append('{k}=$(cat <<EOF\n{v}\nEOF\n)'.format(k=key, v='\n'.join(value)))
                else:
                    cli_vars += '{k}="{v}"\n'.format(k=key,v=value)
        cli_functions = ['{k} {v}'.format(k=key,v=value) for key,value in kwargs.items() if value and key in functions.keys()]
        # Short-circuit the task runner if we're calling functions from the commandline
        if cli_functions:
            for cli_function in cli_functions:
                command = '''
            {dsv}
            {psv}
            {dlv}
            {clv}
            {bfn}
            {clf} {arg} {raw}
                '''.format(
                    dsv='\n'.join(defaults_string_vars),
                    psv=paramset_var,
                    dlv='\n'.join(list_vars),
                    clv=cli_vars,
                    bfn='\n'.join(bash_functions),
                    clf=cli_function,
                    arg=args,
                    raw=raw_args
                )            
                yamlcli.call(command)
        else:
            # Invoke the cli provider
            command = provider_cli.invocation(
                yaml_input_file = yaml_input_file, 
                yaml_vars = yaml_vars,
                bash_functions = bash_functions,
                cli_vars = cli_vars,
                paramset_var = paramset_var,
                default_vars = default_vars,
                string_vars = defaults_string_vars,
                prefix = prefix, 
                debug = __debug, 
                args = args, 
                raw_args=raw_args,
                kwargs = kwargs
            )            
    # Call main cli function
    cli(args)

# Main entry point
if __name__ == '__main__':
    # Are we invoking the run subcommand?
    try:
        arg_run_index = sys.argv.index('run')
    except ValueError:
        arg_run_index = None
    arg_run_index = sys.argv.index('run') if 'run' in sys.argv else None
    # Are we specifing a Taskfile override?
    arg_tf_index = sys.argv.index('-f') if '-f' in sys.argv else None
    tf_override = sys.argv[arg_tf_index + 1] if arg_tf_index else None
    if arg_run_index:
        # Determine the actual run arguments
        run_args = sys.argv[arg_run_index:]
        run_flgs = [a for a in sys.argv[:arg_run_index] if a.startswith('--')]
        cli_args = run_flgs + run_args
        # Hide full stack traces unless invoking the subcommand with debugging enabled
        if not '--debug' in sys.argv:
            func = lambda typ, value, traceback: catchException(logger, script_name, typ, value, traceback)
            sys.excepthook = func        
        if tf_override:
            if any([ext in tf_override for ext in ["yaml","yml"]]):
                # Determine paramter set
                # We only care for a particular pattern of parameters that precede the 'run' subcommand
                paramset = [a for a in sys.argv[1:arg_run_index] if a not in ['run'] and not a.startswith('-')]
                if len(paramset) > 1:
                    paramset = ''.join(paramset[1])
                else:
                    paramset = None
                # Call main function as per parameter set
                if paramset:
                    sys.exit(main(cli_args, param_set=paramset, tasks_file=tf_override))
                else:
                    sys.exit(main(cli_args, tasks_file=tf_override))
            else:
                quit(ERR_ARGS_TASKF_OVERRIDE.format(script=script_name))
        else:
            # Determine paramter set
            paramset = ''.join([a for a in sys.argv[1:arg_run_index] if a not in ['run'] and not a.startswith('-')])
            if paramset:
                sys.exit(main(cli_args, param_set=paramset))
            else:
                sys.exit(main(cli_args))
    else:
        if tf_override:
            demark = sys.argv.index(tf_override)
            run_args = sys.argv[demark + 1:]
            run_flgs = [a for a in sys.argv[:demark] if a.startswith('-') and a != sys.argv[arg_tf_index]]
            cli_args = run_flgs + run_args            
            if any([ext in tf_override for ext in ["yaml","yml"]]):
                # Call main function as per parameter set
                sys.exit(main(cli_args, tasks_file=tf_override))            
            else:
                quit(ERR_ARGS_TASKF_OVERRIDE.format(script=script_name))             
        else:
            sys.exit(main(sys.argv[1:])) 

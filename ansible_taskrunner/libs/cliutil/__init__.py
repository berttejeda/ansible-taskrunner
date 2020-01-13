import logging
import os
import sys

if getattr(sys, 'frozen', False):
    # frozen
    self_file_name = os.path.basename(sys.executable)
else:
    self_file_name = os.path.basename(__file__)
        
# Import third-party and custom modules
try:
    from libs.errorhandler import catchException
    from libs.errorhandler import ERR_ARGS_TASKF_OVERRIDE
except ImportError as e:
    print('Error in %s ' % os.path.basename(self_file_name))
    print('Failed to import at least one required module')
    print('Error was %s' % e)
    print('Please install/update the required modules:')
    print('pip install -U -r requirements.txt')
    sys.exit(1)

# Setup Logging
logger = logging.getLogger(__name__)
if '--debug run' in ' '.join(sys.argv):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

def get_invocation(script_name):
    # Are we invoking the run subcommand?
    arg_run_index = sys.argv.index('run') if 'run' in sys.argv else None
    raw_run_index = sys.argv.index('---raw') if '---raw' in sys.argv else None
    # Are we specifing a Taskfile override (option -f)?
    # If so, make sure this special cli option 
    # occurs before the 'run' subcommand
    arg_tf_index = sys.argv.index('-f') if '-f' in sys.argv else None
    if raw_run_index:
        raw_args = ' '.join(sys.argv[raw_run_index + 1:])
        sys.argv = sys.argv[0:raw_run_index]
    else:
        raw_args = ''
    if arg_tf_index: 
        if arg_run_index:
            if arg_run_index > arg_tf_index:
                arg_tf_index = sys.argv.index('-f')
            else:
                arg_tf_index = None
        else:
            arg_tf_index = sys.argv.index('-f')
    else:
        arg_tf_index = None
    tf_override = sys.argv[arg_tf_index + 1] if arg_tf_index else None
    # Initialize our command-line invocation
    invocation = {
        'param_set': [],
        'tasks_file': 'Taskfile.yaml',
        'tasks_file_override': None,
        'raw_args': raw_args
    }
    if arg_run_index:
        # Determine the actual run arguments
        run_args = sys.argv[arg_run_index:]
        run_flgs = [a for a in sys.argv[:arg_run_index] if a.startswith('--')]
        cli_args = [sys.argv[0]] + run_flgs + run_args
        # Hide full stack traces unless invoking the subcommand
        # with debugging enabled
        if '--debug' not in sys.argv:
            def func(typ, value, traceback): return catchException(
                logger, script_name, typ, value, traceback)
            sys.excepthook = func
        if tf_override:
            if any([ext in tf_override for ext in ["yaml", "yml"]]):
                # Determine paramter set
                # We only care for a particular pattern of parameters
                # that precede the 'run' subcommand
                paramset = [a for a in sys.argv[1:arg_run_index] if a not in ['run'] and not a.startswith('-')]
                if len(paramset) > 1:
                    paramset = paramset[1:]
                else:
                    paramset = []
                # Call main function as per parameter set
                if paramset:
                    invocation['cli'] = cli_args
                    invocation['param_set'] = paramset
                    invocation['tasks_file_override'] = tf_override
                else:
                    invocation['cli'] = cli_args
                    invocation['tasks_file_override'] = tf_override
            else:
                quit(ERR_ARGS_TASKF_OVERRIDE.format(script=script_name))
        else:
            # Determine paramter set
            paramset = [a for a in sys.argv[1:arg_run_index] if a not in ['run'] and not a.startswith('-')]
            if paramset:
                invocation['cli'] = cli_args
                invocation['param_set'] = paramset
            else:
                invocation['cli'] = cli_args
    else:
        if tf_override:
            demark = sys.argv.index(tf_override)
            run_args = sys.argv[demark + 1:]
            run_flgs = [a for a in sys.argv[:demark] if a.startswith(
                '-') and a != sys.argv[arg_tf_index]]
            cli_args = [sys.argv[0]] + run_flgs + run_args
            if any([ext in tf_override for ext in ["yaml", "yml"]]):
                # Call main function as per parameter set
                invocation['cli'] = cli_args
                invocation['tasks_file_override'] = tf_override
            else:
                quit(ERR_ARGS_TASKF_OVERRIDE.format(script=script_name))
        else:
            invocation['cli'] = sys.argv
    logger.debug('CLI Invocation - %s' % invocation)
    return invocation
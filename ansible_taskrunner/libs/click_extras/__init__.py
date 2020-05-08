# Imports
import logging
import os
import re
import sys
from string import Template

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
except ImportError as e:
    print('Error in %s ' % os.path.basename(self_file_name))
    print('Failed to import at least one required module')
    print('Error was %s' % e)
    print('Please install/update the required modules:')
    print('pip install -U -r requirements.txt')
    sys.exit(1)


class ExtendedEpilog(click.Group):
    def format_epilog(self, ctx, formatter):
        """Format click epilog to honor newline characters"""
        if self.epilog:
            formatter.write_paragraph()
            for line in self.epilog.split('\n'):
                formatter.write_text(line)


class ExtendedHelp(click.Command):

    def colorize(self, formatter, color, string):
        if color == 'green':
            formatter.write_text('%s' % click.style(string, fg='bright_green'))
        elif color == 'magenta':
            formatter.write_text('%s' % click.style(string, fg='bright_magenta'))
        elif color == 'red':
            formatter.write_text('%s' % click.style(string, fg='bright_red'))
        elif color == 'yellow':
            formatter.write_text('%s' % click.style(string, fg='bright_yellow'))
        else:
            formatter.write_text(string)

    def format_help(self, ctx, formatter):
        """Format click help to honor newline characters"""
        if self.help:
            formatter.write_paragraph()
            for line in self.help.split('\n'):
                formatter.write_text(line)
        opts = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                opts.append(rv)
        if opts:
            with formatter.section('Options'):
                formatter.write_dl(opts)
        if self.epilog:
            formatter.write_paragraph()
            for line in self.epilog.split('\n'):
                if line:
                    if line.startswith('-'):
                        self.colorize(formatter, 'magenta', line)
                    else:
                        self.colorize(formatter, 'yellow', line)
                else:
                    formatter.write_text(line)

# Allow for mutually-exlusive click options
class NotRequiredIf(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop('not_required_if')
        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs['help'] = (kwargs.get('help', '') +
            ' NOTE: This argument is mutually exclusive with %s' %
            self.not_required_if
        ).strip()
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts
        other_present = self.not_required_if in opts

        if other_present:
            if we_are_present:
                if self.name == self.not_required_if:
                    logger.error("Option order error: `%s`" % self.name)
                    logger.error("Make sure you call this option BEFORE any mutually-exlusive options referencing it")
                    logger.error("Check your tasks manifest")
                    sys.exit(1)
                else:                    
                    logger.error(
                        "Illegal usage: `%s` is mutually exclusive with `%s`" % (
                            self.name, self.not_required_if))
                    sys.exit(1)
            else:
                self.prompt = None

        return super(NotRequiredIf, self).handle_parse_result(
            ctx, opts, args)

class ExtendCLI():
    def __init__(self, parameter_set=None, vars_input={}, help_msg_map={}):
        self.vars = vars_input
        self.help_msg_map = help_msg_map
        self.parameter_set = parameter_set
        self.logger = logger
        # Populate list of available variables for use in internal string Templating
        self.sys_platform = sys.platform
        self.available_vars = vars(self)
        self.available_vars = dict([(v, self.available_vars[v]) for v in self.available_vars.keys() if not type(self.available_vars[v]) == dict])
        pass

    def process_options(self, parameters, func, is_required=False):
        """
        Read dictionary of parameters and translate to click options
        """

        # Account for parameter sets
        vanilla_parameters = dict(
            [(k, v) for k, v in parameters.items() if not isinstance(parameters[k], dict)])
        if self.parameter_set:
            existing_parameter_sets = dict(
                [(k, v) for k, v in parameters.items() if isinstance(parameters[k], dict)])            
            # Exclude parameter sets we have not activated
            excluded_parameter_sets = set(existing_parameter_sets) - set(self.parameter_set)
            for es in excluded_parameter_sets:
                parameters.pop(es)            
            # Build the options dictionary
            for ps in self.parameter_set:
                _parameters = parameters.get(ps, {})
                if _parameters:
                    # Remove the parameter set parent key
                    parameters.pop(ps)
                    # Populate the values from the parameter set
                    parameters.update(_parameters)
        else:
            parameters = vanilla_parameters
        # Variables used in logic for click's variadic arguments (nargs=*)
        numargs = 1
        nargs_ul_is_set = False
        nargs_ul_count = 0
        nargs_ul_count_max = 1
        prompt_if_missing = False
        secure_input = False
        option_type = None
        value_from_env = None
        for cli_option, value in parameters.items():            
            cli_option = Template(cli_option).safe_substitute(**self.available_vars)
            if isinstance(value, list):
                value = [Template(v).safe_substitute(**self.available_vars) if isinstance(v, str) else v for v in value if isinstance(v, (str, int))]
            elif isinstance(value, str):
                value = Template(value).safe_substitute(**self.available_vars)
            else:
                logger.error('Skipping unsupported value type %s' % s)
                continue
            opt_option = None
            opt_option_value = None
            cli_option_is_me = False
            if ' or ' in cli_option:
                cli_option_l = cli_option.split(' or ')
                cli_option = cli_option_l[0]
                opt_option = cli_option_l[1]
                opt_option_value = parameters.get(opt_option, '')
                if not opt_option_value:
                    logger.debug('Skipping mutually exclusive option %s due to possible broken association' % opt_option)
                    continue
            #If a given option is mutually exclusive with another, 
            #then whether or not it is required depends on the
            #command-line invocation relating 
            # to its mutually exclusive partners            
            cli_option_is_me = any(['or %s' % cli_option in o for o,v in parameters.items()])
            cli_option_me_pattern = re.compile(cli_option)
            cli_option_is_called = any([cli_option_me_pattern.match(a) for a in sys.argv])
            cli_option_other = []
            for o,v in parameters.items():
                if 'or %s' % cli_option in o:
                    cli_option_other.append(o.split(' or ')[0])
            len_cli_option_other = len(cli_option_other)
            cli_option_other = '|'.join(cli_option_other)
            cli_option_other_pattern = re.compile(cli_option_other)
            cli_option_other_matches = [cli_option_other_pattern.match(a) for a in sys.argv if cli_option_other_pattern.match(a)]
            cli_option_other_is_called = any(cli_option_other_matches) and len(cli_option_other_matches) == len_cli_option_other
            # Check for option with variadic arguments (nargs=*)
            # There can only be one!
            # Also, make sure we're not treating click.Choice types
            if isinstance(value, list) and '|choice' not in cli_option:
                if len(value) == 1:
                    nargs_ul_is_set = True
                    nargs_ul_count += 1
                    value = str(value[0])
                    numargs = -1
                elif len(value) > 1:
                    if isinstance(value[1], int):
                        numargs = value[1] # e.g. [myvalue,2] would mean the option for myvalue requires 2 args
                    value = str(value[0])
            # Account for click.Choice types
            elif isinstance(value, list):
                option_type = 'choice'
            if self.help_msg_map.get(cli_option):
                option_help = self.help_msg_map[cli_option]
            else:
                option_help = value
            if '|' in cli_option:
                option_strings = cli_option.split('|')
                first_option = option_strings[0].strip()
                second_option = option_strings[1].strip()
                if len(option_strings) > 2:
                    option_tags = [o.strip() for o in option_strings[2:]]
                    if 'prompt' in option_tags:
                        prompt_if_missing = True
                        secure_input = False
                    if 'sprompt' in option_tags:
                        prompt_if_missing = True
                        secure_input = True
                    if 'env' in option_tags:
                        value_from_env = value
                numargs = 1 if numargs < 1 else numargs
                if opt_option:
                    if option_type == 'choice':
                        option = click.option(first_option, second_option, 
                        type=click.Choice(value), help=option_help, cls=NotRequiredIf,
                        prompt=prompt_if_missing, hide_input=secure_input, not_required_if=opt_option_value,
                        envvar=value_from_env)
                    else:
                        option = click.option(first_option, second_option, value, 
                        type=str, nargs=numargs, help=option_help, cls=NotRequiredIf,
                        prompt=prompt_if_missing, hide_input=secure_input, not_required_if=opt_option_value,
                        envvar=value_from_env)
                else:
                    if cli_option_is_me and cli_option_other_is_called:
                        _is_required = False
                    else:
                        _is_required = is_required
                    if option_type == 'choice':
                        option = click.option(first_option, second_option, 
                        type=click.Choice(value), help=option_help, 
                        prompt=prompt_if_missing, hide_input=secure_input, required=_is_required,
                        envvar=value_from_env)
                    else:
                        option = click.option(first_option, second_option, 
                        value, type=str, nargs=numargs, help=option_help, 
                        prompt=prompt_if_missing, hide_input=secure_input, required=_is_required,
                        envvar=value_from_env)
            else:
                if nargs_ul_is_set and \
                not nargs_ul_count > nargs_ul_count_max:
                    option = click.argument(
                        cli_option, value, help=option_help, 
                        nargs=numargs, prompt=prompt_if_missing, hide_input=secure_input, required=is_required,
                        envvar=value_from_env)
                else:
                    numargs = 1 if numargs < 1 else numargs
                    if opt_option:
                        option = click.option(
                            cli_option, value, cls=NotRequiredIf,
                            is_flag=True, default=False, 
                            help=option_help, not_required_if=opt_option_value,
                            envvar=value_from_env)
                    else:
                        if cli_option_is_me and cli_option_other_is_called:
                            _is_required = False
                        else:
                            _is_required = is_required
                        option = click.option(
                            cli_option, value, is_flag=True, 
                            default=False, help=option_help, 
                            required=_is_required, envvar=value_from_env)
            try:
                func = option(func)
            except Exception as e:
                logger.error('I had a problem parsing your parameters, error was %s' % e)
                continue
            option_type = None
            prompt_if_missing = False
            secure_input = False
            value_from_env = None
            nargs_ul_is_set = False
            numargs = 1
        return func

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
        required_parameters = self.vars.get('required_parameters', {})
        if not required_parameters:
            required_parameters = {}
        else:
            param_list = list(required_parameters.items())
            # Filter out any None/Null values
            # Accounting for mutually exclusive options
            for param in param_list:
                if param[0] != 'or' and param[1] is None:
                    logger.debug("Removing invalid option key '%s'" % param[0])
                    required_parameters.pop(param[0])
        extended_cli_func_required = self.process_options(
            required_parameters, func, is_required=True)
        optional_parameters = self.vars.get('optional_parameters', {})
        if not optional_parameters:
            optional_parameters = {}
        else:
            param_list = list(optional_parameters.items())
            # Filter out any None values
            # Accounting for mutually exclusive options
            for param in param_list:
                if param[0] != 'or' and param[1] is None:
                    logger.debug("Removing invalid option key '%s'" % param[0])
                    optional_parameters.pop(param[0])
        extended_cli_func = self.process_options(
            optional_parameters, extended_cli_func_required)
        return extended_cli_func

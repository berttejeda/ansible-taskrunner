# Imports
import logging
import re
import sys
from string import Template

# Setup Logging
logger = logging.getLogger(__name__)
if '--debug run' in ' '.join(sys.argv):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# Import third-party and custom modules
try:
    import click
except ImportError as e:
    print('Failed to import at least one required module')
    print('Error was %s' % e)
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
        for cli_option, value in parameters.items():
            cli_option = Template(cli_option).safe_substitute(**self.available_vars)
            value = Template(value).safe_substitute(**self.available_vars)
            opt_option = None
            opt_option_value = None
            cli_option_is_me = False
            if ' or ' in cli_option:
                cli_option_l = cli_option.split(' or ')
                cli_option = cli_option_l[0]
                opt_option = cli_option_l[1]
                opt_option_value = parameters.get(opt_option, '')
                if not opt_option_value:
                    logger.warning('Skipping mutually exclusive option %s due to possible broken association' % opt_option)
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
            if isinstance(value, list):
                if len(value) == 1:
                    nargs_ul_is_set = True
                    nargs_ul_count += 1
                    value = str(value[0])
                    numargs = -1
                elif len(value) > 1:
                    numargs = value[1]
                    value = str(value[0])
            if self.help_msg_map.get(cli_option):
                option_help = self.help_msg_map[cli_option]
            else:
                option_help = value
            if '|' in cli_option:
                option_string = cli_option.split('|')
                first_option = option_string[0].strip()
                second_option = option_string[1].strip()
                numargs = 1 if numargs < 1 else numargs
                if opt_option:
                    option = click.option(first_option, second_option, value, 
                    type=str, nargs=numargs, help=option_help, cls=NotRequiredIf,
                    not_required_if=opt_option_value)
                else:
                    if cli_option_is_me and cli_option_other_is_called:
                        _is_required = False
                    else:
                        _is_required = is_required
                    option = click.option(first_option, second_option, 
                    value, type=str, nargs=numargs, help=option_help, 
                    required=_is_required)
            else:
                if nargs_ul_is_set and \
                not nargs_ul_count > nargs_ul_count_max:
                    option = click.argument(
                        cli_option, value, help=option_help, 
                        nargs=numargs, required=is_required)
                else:
                    numargs = 1 if numargs < 1 else numargs
                    if opt_option:
                        option = click.option(
                            cli_option, value, cls=NotRequiredIf,
                            is_flag=True, default=False, 
                            help=option_help, 
                            not_required_if=opt_option_value)
                    else:
                        if cli_option_is_me and cli_option_other_is_called:
                            _is_required = False
                        else:
                            _is_required = is_required
                        option = click.option(
                            cli_option, value, is_flag=True, 
                            default=False, help=option_help, 
                            required=_is_required)
            func = option(func)
            nargs_ul_is_set = False
            numargs = 1
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
                    logger.warning("Removing invalid option key '%s'" % param[0])
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
                    logger.warning("Removing invalid option key '%s'" % param[0])
                    optional_parameters.pop(param[0])
        # Filter out any None values
        extended_cli_func = self.process_options(
            optional_parameters, extended_cli_func_required)
        return extended_cli_func

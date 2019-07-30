# Imports
import logging
import sys

# Logging
logger = logging.getLogger('logger')
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


class ExtendCLI():
    def __init__(self, parameter_set=None, vars_input={}, help_msg_map={}):
        self.vars = vars_input
        self.help_msg_map = help_msg_map
        self.parameter_set = parameter_set
        self.logger = logger
        pass

    def process_options(self, parameters, func, is_required=False):
        """
        Read dictionary of parameters and translate to click options
        """

        # Account for parameter sets
        vanilla_parameters = dict(
            [(k, v) for k, v in parameters.items() if not isinstance(parameters[k], dict)])
        if self.parameter_set:
            _parameters = parameters.get(self.parameter_set, {})
            if _parameters:
                parameters = {}
                parameters.update(vanilla_parameters)
                parameters.update(_parameters)
        else:
            parameters = vanilla_parameters
        # Variables used in logic for click's variadic arguments (nargs=*)
        numargs = 1
        nargs_ul_is_set = False
        nargs_ul_count = 0
        nargs_ul_count_max = 1
        for cli_option, value in parameters.items():
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
                option = click.option(first_option, second_option, 
                    value, type=str, nargs=numargs, help=option_help, 
                    required=is_required)
            else:
                if nargs_ul_is_set and \
                not nargs_ul_count > nargs_ul_count_max:
                    option = click.argument(
                        cli_option, value, help=option_help, 
                        nargs=numargs, required=is_required)
                else:
                    numargs = 1 if numargs < 1 else numargs
                    option = click.option(
                        cli_option, value, is_flag=True, 
                        default=False, help=option_help, 
                        required=is_required)
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
            # Filter out any None values
            for k,v in required_parameters.items():
                if v is None:
                    logger.warning("Invalid option key '%s'" % k)
                    del required_parameters[k]
        extended_cli_func_required = self.process_options(
            required_parameters, func, is_required=True)
        optional_parameters = self.vars.get('optional_parameters', {})
        if not optional_parameters:
            optional_parameters = {}
        else:
            # Filter out any None values
            for k,v in optional_parameters.items():
                if v is None:
                    logger.warning("Invalid option key '%s'" % k)
                    del optional_parameters[k]
        # Filter out any None values
        extended_cli_func = self.process_options(
            optional_parameters, extended_cli_func_required)
        return extended_cli_func

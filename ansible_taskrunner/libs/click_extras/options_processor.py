# Imports
import re
import sys
from string import Template

# Import third-party and custom modules
from ansible_taskrunner.logger import Logger
from ansible_taskrunner.libs.click_extras.options_advanced import NotRequiredIf
import click

logger_obj = Logger()
logger = logger_obj.init_logger(__name__)

class ExtendCLIOptionsProcessor():

    def process_option_w_arg(self, **kwargs):
        cli_option = kwargs.get('cli_option')
        is_required = kwargs.get('is_required')
        cli_option_is_me = kwargs.get('cli_option_is_me')
        value = kwargs.get('value')
        cli_option_other_is_called = kwargs.get('cli_option_other_is_called')
        numargs = kwargs.get('numargs')
        opt_option = kwargs.get('opt_option')
        option_help = kwargs.get('option_help')
        opt_option_value = kwargs.get('opt_option_value')
        option_type = kwargs.get('option_type')
        secure_input = kwargs.get('secure_input')
        prompt_if_missing = kwargs.get('prompt_if_missing')
        value_from_env = kwargs.get('value_from_env')
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
                                      prompt=prompt_if_missing, hide_input=secure_input,
                                      not_required_if=opt_option_value,
                                      envvar=value_from_env)
            else:
                option = click.option(first_option, second_option, value,
                                      type=str, nargs=numargs, help=option_help, cls=NotRequiredIf,
                                      prompt=prompt_if_missing, hide_input=secure_input,
                                      not_required_if=opt_option_value,
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
        return option

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
        for cli_o_name, value in parameters.items():

            cli_option = Template(cli_o_name).safe_substitute(**self.available_vars)

            if cli_option not in self.seen_options:
                self.seen_options.add(cli_option)
            else:
                if logger.level == 10:
                    logger.warning(f"Not adding {cli_option}: {value} because it is a duplicate option")
                continue

            if self.help_msg_map.get(cli_option):
                option_help = self.help_msg_map[cli_option]
            else:
                option_help = value
            if isinstance(value, list):
                value = [Template(v).safe_substitute(**self.available_vars) if isinstance(v, str) else v for v in value if isinstance(v, (str, int))]
            elif isinstance(value, str):
                value = Template(value).safe_substitute(**self.available_vars)
            else:
                logger.debug(f'Skipping unsupported value type for {value} ({type(value)})')
                continue
            opt_option = None
            opt_option_value = None
            if ' or ' in cli_option:
                cli_option_l = cli_option.split(' or ')
                cli_option = cli_option_l[0]
                opt_option = cli_option_l[1]
                opt_option_value = parameters.get(opt_option, '')
                if not opt_option_value:
                    logger.debug(f'Skipping mutually exclusive option {opt_option} due to possible broken association')
                    continue
            # If a given option is mutually exclusive with another,
            # then whether it is required depends on the
            # command-line invocation relating
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
            if '|' in cli_option:
                # TODO possibly use self to move away from duplicating parameters
                option_settings = {
                    "cli_option": cli_option,
                    "is_required": is_required,
                    "cli_option_is_me": cli_option_is_me,
                    "value": value,
                    "cli_option_other_is_called": cli_option_other_is_called,
                    "numargs": numargs,
                    "opt_option": opt_option,
                    "option_help": option_help,
                    "opt_option_value": opt_option_value,
                    "option_type": option_type,
                    "prompt_if_missing": prompt_if_missing,
                    "secure_input": secure_input,
                    "value_from_env": value_from_env
                }
                option = self.process_option_w_arg(**option_settings)
            else:
                # TODO break this out into a separate function like above
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
                        # For a flag to be required, both the following must be set
                        # default=None
                        # required=True
                        if _is_required:
                            default_value=None
                        else:
                            default_value=False
                        option = click.option(
                            cli_option, value, is_flag=True,
                            default=default_value, help=option_help,
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

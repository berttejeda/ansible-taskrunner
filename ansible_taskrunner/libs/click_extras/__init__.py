# Imports
import click
import sys
from ansible_taskrunner.logger import Logger
from ansible_taskrunner.libs.click_extras.options_advanced import MutuallyExclusiveOption
from ansible_taskrunner.libs.click_extras.options_advanced import RequiredIf
from ansible_taskrunner.libs.click_extras.options_advanced import NotRequiredIf
from bertdotconfig.configutils import AttrDict
from string import Template

logger_obj = Logger()
logger = logger_obj.init_logger(__name__)

class ExtendCLI():

    def __init__(self, **kwargs):

        self.parameter_set = kwargs.get('parameter_set')
        global_options = kwargs.get('global_options', {})
        self.command_vars = kwargs.get('command_vars', {})
        self.command_option_map = {}
        # Merge in global options
        AttrDict.merge(self.command_vars, {'options': global_options})
        self.help_msg_map = kwargs.get('help_msg_map', {})
        self.available_vars = kwargs.get('available_vars', {})
        # Populate list of available variables for use in internal string Templating
        self.sys_platform = sys.platform
        self.default_option_class = click.Option

        self.seen_options = set()
        self.click_type_map = {
        "str": click.STRING,
        "int": click.INT,
        "float": click.FLOAT,
        "bool": click.BOOL,
        "path": click.Path,
        "choice": click.Choice,
        }
        self.click_option_class_map = {
            'mutually_exclusive': MutuallyExclusiveOption,
            'required_if': RequiredIf,
            'not_required_if': NotRequiredIf,
        }

    def get_option_type(self, opt):
        if opt.get("type", "str") == "choice":
            opt_choices = opt.get("options", [])
            opt_choices_templated = [Template(c).safe_substitute(**self.available_vars) if isinstance(c, str) else c for c in opt_choices if isinstance(c, (str, int))]
            return self.click_type_map["choice"](opt_choices_templated)
        return self.click_type_map[opt.get("type", "str")]

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

        command_option_map = {}
        for k,v in self.command_vars.options.items():
            long_opt = v.get('long')
            short_opt = v.get('short')
            if long_opt and short_opt:
                command_option_map[v['var']] = f"{long_opt}|{short_opt}"
            elif long_opt:
                command_option_map[v['var']] = f"{long_opt}"
            elif short_opt:
                command_option_map[v['var']] = f"{short_opt}"

        for option_name, option in self.command_vars.get('options', {}).items():

            option_name = Template(option_name).safe_substitute(**self.available_vars)

            param_declarations = []

            long_option = option.get("long", None)
            if long_option:
                param_declarations.append(long_option)

            short_option = option.get("short", None)
            if short_option:
                param_declarations.append(short_option)

            if not any([long_option, short_option]):
                logger.error(f'Skipping option {option_name} - found no short or long option!')
                continue

            option_variable = option.get("var", None)
            option_nargs = option.get("nargs", 1)
            option_help = option_help_effective = Template(option.get('help', '')).safe_substitute(**self.available_vars)
            option_show_default = bool(option.get('show_default', False))
            option_prompt = bool(option.get('prompt', False))
            option_prompt_required = bool(option.get('prompt_required', False))
            option_confirm_prompt = bool(option.get('confirm_prompt', False))
            option_secure = bool(option.get('secure', False))
            option_required = bool(option.get('required', False))
            option_is_flag = bool(option.get('is_flag', False))
            option_is_hidden = bool(option.get('is_hidden', False))
            option_show_choices = bool(option.get('show_choices', True))
            option_show_envvar = bool(option.get('env_var_show', True))
            option_supports_counting = bool(option.get('allow_counting', False))
            option_supports_multiple = bool(option.get('allow_multiple', False))
            option_value_from_env = option.get('env_var', None)
            mutually_exclusive_with = option.get('mutually_exclusive_with', '')
            required_if = option.get('required_if', '')
            not_required_if = option.get('not_required_if', '')

            if mutually_exclusive_with and option_required:
                logger.warning(f"Not honoring mutual exclusivity of option '{option_name}' " + \
                               f"and options with variables {mutually_exclusive_with}, as 'required' must be False")
                option_class = self.default_option_class
                special_options = {}
            elif mutually_exclusive_with and not option_required:
                option_class = self.click_option_class_map['mutually_exclusive']
                special_options = {'mutually_exclusive': mutually_exclusive_with}
                ex_strs = [command_option_map.get(f,'') for f in mutually_exclusive_with]
                ex_str = ', '.join(ex_strs)
                if ex_str:
                    option_help_effective = option_help + \
                    f' NOTE: This argument is mutually exclusive with [{ex_str}]'
                else:
                    option_help_effective = ''
            elif required_if:
                option_class = self.click_option_class_map['required_if']
                special_options = {'required_if': required_if}
                ex_strs = [command_option_map.get(f,'') for f in required_if]
                ex_str = ', '.join(ex_strs)
                if ex_str:
                    option_help_effective = option_help + \
                    f' NOTE: This argument is mutually inclusive with [{ex_str}]'
                else:
                    option_help_effective = ''
            elif not_required_if:
                option_class = self.click_option_class_map['not_required_if']
                special_options = {'not_required_if': not_required_if}
                ex_strs = [command_option_map.get(f, '') for f in not_required_if]
                ex_str = ', '.join(ex_strs)
                if ex_str:
                    option_help_effective = option_help + \
                    f' NOTE: This argument is optional when related options are specified: [{ex_str}]'
                else:
                    option_help_effective = ''
            else:
                option_class = self.default_option_class
                special_options = {}

            option = click.option(
                *param_declarations,
                option_variable,
                cls=option_class,
                confirmation_prompt=option_confirm_prompt,
                count=option_supports_counting,
                envvar=option_value_from_env,
                nargs=option_nargs,
                help=option_help_effective,
                hide_input=option_secure,
                hidden=option_is_hidden,
                is_flag=option_is_flag,
                prompt=option_prompt,
                prompt_required=option_prompt_required,
                multiple=option_supports_multiple,
                required=option_required,
                show_choices=option_show_choices,
                show_envvar=option_show_envvar,
                show_default=option_show_default,
                type=self.get_option_type(option),
                **special_options,
            )
            func = option(func)
        return func

# Imports
import click
import sys
from ansible_taskrunner.logger import Logger
from ansible_taskrunner.libs.click_extras.options_advanced import MutuallyExclusiveOption, NotRequiredIf
from bertdotconfig.configutils import AttrDict
from string import Template

logger_obj = Logger()
logger = logger_obj.init_logger(__name__)

class ExtendCLI():

    def __init__(self, **kwargs):

        self.parameter_set = kwargs.get('parameter_set')
        global_options = kwargs.get('global_options', {})
        self.command_vars = kwargs.get('command_vars', {})
        # Merge in global options
        AttrDict.merge(self.command_vars, {'options': global_options})
        self.help_msg_map = kwargs.get('help_msg_map', {})
        self.available_vars = kwargs.get('available_vars', {})
        # Populate list of available variables for use in internal string Templating
        self.sys_platform = sys.platform
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
            'not_required_if': NotRequiredIf,
        }
        # self.click_option_class_options_map = {
        #     'mutually_exlusive': MutuallyExclusiveOption,
        #     'not_required_if': not_required_if,
        # }

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
            option_help = Template(option.get('help', '')).safe_substitute(**self.available_vars)
            option_prompt = bool(option.get('prompt', False))
            option_secure = bool(option.get('secure', False))
            option_required = bool(option.get('required', False))
            option_is_flag = bool(option.get('is_flag', False))
            option_value_from_env = option.get('env_var', None)
            mutually_exlusive_with = option.get('mutually_exlusive_with', '')
            not_required_if = option.get('not_required_if', '')

            if mutually_exlusive_with and option_required:
                logger.warning(f"Not honoring mutual exclisivity of opiton '{option_name}' " + \
                               f"and options with variables {mutually_exlusive_with}, as both are set to required")
                option_class = click.Option
                special_options = {}
            elif mutually_exlusive_with and not option_required:
                option_class = self.click_option_class_map['mutually_exclusive']
                special_options = {'mutually_exclusive': mutually_exlusive_with}
            elif not_required_if:
                option_class = self.click_option_class_map['not_required_if']
                special_options = {'not_required_if': not_required_if}
            else:
                option_class = click.Option
                special_options = {}

            option = click.option(
                *param_declarations,
                option_variable,
                cls=option_class,
                type=self.get_option_type(option),
                nargs=option_nargs,
                help=option_help,
                prompt=option_prompt,
                hide_input=option_secure,
                required=option_required,
                is_flag=option_is_flag,
                envvar=option_value_from_env,
                **special_options,
            )
            func = option(func)
        return func

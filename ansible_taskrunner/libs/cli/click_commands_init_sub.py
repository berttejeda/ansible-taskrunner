# Import builtins
from string import Template

# Import third-party and custom modules
from ansible_taskrunner.libs.click_extras.help import ExtendedHelp
from ansible_taskrunner.defaults import shell_invocation_mappings
from ansible_taskrunner.logger import Logger


logger_obj = Logger()
logger = logger_obj.init_logger(__name__)

class CLICK_Commands_SUB_INIT:

  def init_cli_sub_command(self, cli_obj, cli, **kwargs):

    # Force bastion mode if running from a Windows host
    if self.is_windows or kwargs.get('_bastion_mode', False):
        bastion_settings = {
          'config_file': self.config.get('bastion_mode.config_file', 'sftp-config.json'),
          # Turn bastion Mode off if we explicitly don't want it
          'enabled': self.config.get('bastion_mode.enabled', True),
          'keep_alive': self.config.get('bastion_mode.keep_alive', True),
          'poll_wait_time': self.config.get('bastion_mode.poll_wait_time', 5),
          'sftp_sync': self.config.get('bastion_mode.sync', True)
        }
    else:
        bastion_settings = {}

    commands = kwargs['commands']

    for c, o in commands.items():
        # Parse help documentation
        _help_string = cli_obj.yaml_vars.get(f'commands.{c}.help.message', '')
        help_string = Template(_help_string).safe_substitute(**cli_obj.available_vars)
        examples = cli_obj.yaml_vars.get(f'commands.{c}.help.examples', '')
        examples_string = ''
        epilog = ''
        command_name = Template(c).safe_substitute(**self.available_vars)
        if isinstance(examples, list):
            for example in examples:
                if isinstance(example, dict):
                    for key, value in example.items():
                        value = Template(value).safe_substitute(**cli_obj.available_vars)
                        examples_string += '\n- {k}:\n{v}'.format(k=key, v=value)
                if isinstance(example, str):
                    example = Template(example).safe_substitute(**cli_obj.available_vars)
                    examples_string += f'{example}\n'
        # Shell functions
        shell_functions = []
        internal_functions = cli_obj.yaml_vars.get(f'commands.{c}.functions', {})
        if internal_functions:
            # Append the special make_mode_engage bash function
            internal_functions['embedded_function_targets'] = {
                'help': 'Invoke Embedded Function',
                'shell': 'bash',
                'hidden': 'true',
                'source': '''
            echo "Invoking embedded function '${1}'"
            ${1}
            '''
            }
            for f_n, f_s in internal_functions.items():
                f_shell = f_s.get(f'shell', {})
                source = f_s.get(f'source', {})
                if f_shell and source:
                    function_source = shell_invocation_mappings[f_shell].format(src=source)
                    shell_functions.append(
                        f'function {f_n}(){{\n{function_source}\n}}'
                    )

        epilog_string = cli_obj.yaml_vars.get(f'commands.{c}.help.epilog', '')

        if epilog_string:
            shell_function_help_string = ''
            for f_n, f_s in internal_functions.items():
                is_hidden = internal_functions.get(f'{f_n}.hidden', False)
                if is_hidden:
                    continue
                else:
                    f_help_string = internal_functions.get(f'{f_n}.help', '')
                    shell_function_help_string += f'{f_n}: {f_help_string}\n'
            epilog = f"{epilog_string}\n" + \
                     f"Examples:\n{examples_string or 'None'}\n\n" + \
                     f"Available shell functions:\n\n{shell_function_help_string or 'None'}"
            epilog = Template(epilog).safe_substitute(**cli_obj.available_vars)

        command_vars = cli_obj.yaml_vars.get(f'commands.{c}')

        provider_vars = {}
        # Define the list of yaml variables, excluding the 'inventory' variable (if applicable)
        yaml_variables = [(key, value) for key, value in self.yaml_vars.items()]
        yaml_variables_wo_jinja = dict(
            [
                (t[0], t[1]) for t in yaml_variables
                if not self.skip_values_pattern.search(str(t[1])) and
                   not self.skip_keys_pattern.search(str(t[0]))
            ]
        )

        special_vars = dict(
            [
                (t[0], t[1]) for t in yaml_variables
                if self.special_vars_pattern.search(str(t[0]))
            ]
        )

        extra_vars = special_vars.get('ANSIBLE_EXTRA_VARS', [])
        # Add the k,v for __tasks_file__
        provider_vars['__tasks_file__'] = self.tf_path
        # Add the k,v for __command__
        provider_vars['__command__'] = command_name
        # Gather any references to extra vars
        extra_vars_cli_string = ''.join(f'-e @{e} ' for e in extra_vars)
        extra_vars_string = f'\nextra_vars="{extra_vars_cli_string}"'

        cli_sub_kwargs = {
            'bastion_settings': bastion_settings,
            'command_vars': command_vars,
            'extra_vars_cli_string': extra_vars_cli_string,
            'extra_vars_string': extra_vars_string,
            'function_ref': '_f',
            'internal_functions': internal_functions,
            'provider_vars': provider_vars,
            'shell_functions': shell_functions,
            'yaml_variables_wo_jinja': yaml_variables_wo_jinja
        }
        f = cli_obj.create_cli_sub_command(**cli_sub_kwargs)
        _f = cli.command(name=command_name, cls=ExtendedHelp, help="{h}".format(h=help_string), epilog=epilog)(f)


# Import builtins
from string import Template

# Import third-party and custom modules
from ansible_taskrunner.libs.click_extras import ExtendedHelp
from ansible_taskrunner.libs.proc_mgmt import shell_invocation_mappings
from ansible_taskrunner.logger import Logger


logger_obj = Logger()
logger = logger_obj.init_logger(__name__)

class CLICK_Commands_SUB_INIT:

  def init_cli_sub_command(self, cli_obj, cli, **kwargs):

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
                        examples_string += '- {k}:\n{v}'.format(k=key, v=value)
                if isinstance(example, str):
                    example = Template(example).safe_substitute(**cli_obj.available_vars)
                    examples_string += '%s\n' % example
        # Shell functions
        shell_functions = []
        internal_functions = cli_obj.yaml_vars.get(f'commands.{c}.functions', {})
        if internal_functions:
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
                f_hidden_functions = internal_functions.get(f'{f_n}.hidden', {})
                f_help = internal_functions.get(f'{f_n}.help', {})
                if f_hidden_functions or f_help:
                    continue
                else:
                    f_help_string = internal_functions[f].get('help')
                    shell_function_help_string += f'{f}: {f_help_string}\n'
            epilog = f"{epilog_string}\nExamples:\n\n{examples_string or 'None'}\n\nAvailable shell functions:\n\n{shell_function_help_string or 'None'}"
            epilog = Template(epilog).safe_substitute(**cli_obj.available_vars)

        command_vars = cli_obj.yaml_vars.get(f'commands.{c}')

        f = cli_obj.create_cli_sub_command(
            function_ref='_f',
            command_name=command_name,
            command_vars=command_vars,
            taskfile_vars=self.yaml_vars,
            shell_functions=shell_functions,
            internal_functions=internal_functions
        )
        _f = cli.command(name=command_name, cls=ExtendedHelp, help="{h}".format(h=help_string), epilog=epilog)(f)


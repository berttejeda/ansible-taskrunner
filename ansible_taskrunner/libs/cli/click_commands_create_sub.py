# Import builtins

# Import third-party and custom modules
import click
from bertdotconfig.configutils import AttrDict
from ansible_taskrunner.libs.click_extras import ExtendCLI
from ansible_taskrunner.logger import Logger
import json
logger_obj = Logger()
logger = logger_obj.init_logger(__name__)

class CLICK_Commands_SUB:

  def create_cli_sub_command(self, **kwargs):

    bastion_settings = kwargs['bastion_settings']
    command_vars = kwargs.get('command_vars', {})
    extra_vars_cli_string = kwargs['extra_vars_cli_string']
    extra_vars_string = kwargs['extra_vars_string']
    internal_functions = kwargs['internal_functions']
    function_ref = kwargs['function_ref']
    shell_functions = kwargs.get('shell_functions', [])
    provider_vars = kwargs['provider_vars']
    yaml_variables_wo_jinja = kwargs['yaml_variables_wo_jinja']

    extend_cli = ExtendCLI(
        available_vars=self.available_vars,
        parameter_set=self.param_set,
        global_options=self.global_options,
        command_vars=command_vars,
        help_msg_map=self.option_help_messages)

    @click.option('---make', 'make_mode_engage', is_flag=True,
                  help='Call shell function')
    @click.option('---echo',
                  is_flag=True,
                  help="Don't run, simply echo underlying commands")
    @extend_cli.options
    @extend_cli.bastion_mode
    @self.provider_cli.options
    def func(args=None, **kwargs):
      # Process Raw Args
      # Process run args, if any
      args = ' '.join(args) if args else ''
      # Silence Output if so required
      # Initialize values for subshell
      prefix = 'echo' if kwargs.get('_echo') else ''

      # Make provider vars available to templating
      AttrDict.merge(provider_vars, kwargs)
      AttrDict.merge(provider_vars, yaml_variables_wo_jinja)
      AttrDict.merge(self.available_vars, provider_vars)

      provider_vars_sanitized = provider_vars

      # Process complex variables
      for key, value in list(provider_vars_sanitized.items()):
          if value is None:
              value = ''
          if isinstance(value, bool):
              value = str(value)
          if '\n' in str(value):
              value = value.split('\n')
          if value and key not in internal_functions.keys():
              if isinstance(value, list) or isinstance(value, tuple):
                  try:
                      if key == 'inventory':
                          value_string = '\n'.join(value)
                          provider_vars_sanitized[key] = f'$(cat <<EOF\n{value_string}\nEOF\n)'
                      else:
                          value_string = '\n'.join(value).replace("'", "\'").replace('"', '\"')
                          provider_vars_sanitized[key] = f"'{value_string}'"
                  except TypeError as e:
                      if logger.level == 10:
                          logger.error(f"Unsupported variable type, skipped variable {key}")
                          logger.error(f"Skip Reason {e}")
              elif isinstance(value, dict):
                  value_string = json.dumps(value)
                  provider_vars_sanitized[key] = f'$(cat <<EOF\n{value_string}\nEOF\n)'
      # We don't want to 'commands' or 'inventory' down to the subprocess
      provider_vars_sanitized.pop('commands')
      # Derive the provider vars string from provider vars
      provider_vars_string_block = '\n'.join([f'{k}={v}' for k, v in provider_vars_sanitized.items()]) + extra_vars_string

      cli_functions = ['{k} {v}'.format(
          k=key, v='' if value in [True, False] else value) for key, value in kwargs.items() if
          value and key in internal_functions.keys()]

      if cli_functions:
          bf = '\n'.join(shell_functions)
          cf = '\n'.join(cli_functions)
          command = f"{provider_vars_string_block}\n{bf}\n{cf} {args} {self.raw_args}"
          if prefix == 'echo':
              print(command)
          else:
              self.sub_process.call(command, debug_enabled=self.debug, suppress_output=self.suppress_output)
      else:
          self.provider_cli.invocation(
              args=args,
              available_vars=self.available_vars,
              bastion_settings=bastion_settings,
              debug=self.debug,
              extra_vars=extra_vars_cli_string,
              invocation=self.cli_invocation,
              prefix=prefix,
              provider_vars=provider_vars_sanitized,
              provider_vars_string_block=provider_vars_string_block,
              raw_args=self.raw_args,
              shell_functions=shell_functions,
              suppress_output=self.suppress_output,
              yaml_input_file=self.tf_path
          )
          # Invoke the cli provider
    func.__name__ = function_ref
    return func

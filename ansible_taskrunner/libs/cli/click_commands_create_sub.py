# Import builtins

# Import third-party and custom modules
import click
from bertdotconfig.configutils import AttrDict
from ansible_taskrunner.libs.click_extras import ExtendCLI
from ansible_taskrunner.defaults import bool_strings
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
    shell_functions = '\n'.join(kwargs.get('shell_functions', []))
    provider_vars = kwargs['provider_vars']
    yaml_variables_wo_jinja = kwargs['yaml_variables_wo_jinja']

    extend_cli = ExtendCLI(
        available_vars=self.available_vars,
        parameter_set=self.param_set,
        global_options=self.global_options,
        command_vars=command_vars,
        help_msg_map=self.option_help_messages)

    @click.option('---invoke-function', 'embedded_function_targets',
                  help='Call shell functions')
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
          if '\n' in str(value) and key == 'inventory_expression':
              value = value.split('\n')
          if str(value).lower() in bool_strings:
              value = bool(value)
          if value and key not in internal_functions.keys():
              if isinstance(value, str):
                if '\n' in value and key != 'inventory_expression':
                    value_string = json.dumps(value)
                    provider_vars_sanitized[key] = f'$(cat <<EOF\n{value_string}\nEOF\n)'
                else:
                    provider_vars_sanitized[key] = f'"{value}"'
              elif type(value) in [AttrDict, dict, list, tuple]:
                  try:
                      if key == 'inventory_expression':
                          value_string = '\n'.join(value)
                          provider_vars_sanitized[key] = f'$(cat <<EOF\n{value_string}\nEOF\n)'
                      else:
                          value_string = json.dumps(value)
                          provider_vars_sanitized[key] = f'$(cat <<EOF\n{value_string}\nEOF\n)'
                  except TypeError as e:
                      if logger.level == 10:
                          logger.error(f"Unsupported variable type, skipped variable {key}")
                          logger.error(f"Skip Reason {e}")
              else:
                  provider_vars_sanitized[key] = value
      # We don't want to 'commands' or 'inventory' down to the subprocess
      provider_vars_sanitized.pop('commands', '')
      provider_vars_sanitized.pop('environment_vars', '')
      # Derive the provider vars string from provider vars
      exports = self.yaml_vars.get('environment_vars', {})
      if isinstance(exports, dict):
        exports_string = '\n'.join([f'export {key}="{value}"' for key, value in exports.items() if value])
      else:
        exports_string = f'environment_vars={exports}'
      provider_vars_string_block = '\n'.join(['{k}={v}'.format(k=key, v='""' if value == None else value) for key, value in provider_vars_sanitized.items()]) + \
                                   f'\n{exports_string}\n' + \
                                   extra_vars_string
      cli_functions = ['{f} {a}'.format(f=fnc, a=arg if arg and arg not in ['True', 'False'] else '') for fnc,arg in kwargs.items() if fnc in internal_functions.keys() and arg]

      self.provider_cli.invocation(
          args=args,
          available_vars=self.available_vars,
          cli_functions=cli_functions,
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
          yaml_input_file=self.tf_path,
          sub_process=self.sub_process
      )
      # Invoke the cli provider
    func.__name__ = function_ref
    return func

# Import builtins
from collections import OrderedDict
import sys

# Import third-party and custom modules
import click
from ansible_taskrunner.libs.click_extras import ExtendCLI
from ansible_taskrunner.logger import Logger
from bertdotconfig.configutils import AttrDict

logger_obj = Logger()
logger = logger_obj.init_logger(__name__)

class CLICK_Commands_SUB:

  def create_cli_sub_command(self, **kwargs):

    function_ref = kwargs['function_ref']
    command_name = kwargs['command_name']
    command_vars = kwargs.get('command_vars', {})
    taskfile_vars = kwargs.get('taskfile_vars', {})
    shell_functions = kwargs.get('shell_functions', [])
    internal_functions = kwargs.get('internal_functions', {})
    is_windows = kwargs.get('is_windows', False)
    extend_cli = ExtendCLI(
        available_vars=self.available_vars,
        parameter_set=self.param_set,
        global_options=self.global_options,
        command_vars=command_vars,
        help_msg_map=self.option_help_messages)

    @click.option('---make', 'make_mode_engage', is_flag=False,
                  help='Call shell function',
                  required=False)
    @click.option('---echo',
                  is_flag=True,
                  help='Don\'t run, simply echo underlying commands')
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
      # Are we executing commands via bastion host?
      bastion_settings = {}
      # Force bastion mode if running from a Windows host
      bastion_mode_enabled = True if is_windows else kwargs.get('_bastion_mode', False)
      if bastion_mode_enabled:
          bastion_settings = {
          'config_file': self.config.get('bastion_mode.config_file', 'sftp-config.json'),
          # Turn bastion Mode off if we explicitly don't want it
          'enabled': self.config.get('bastion_mode.enabled', True),
          'keep_alive': self.config.get('bastion_mode.keep_alive', True),
          'poll_wait_time': self.config.get('bastion_mode.poll_wait_time', 5),
          'sftp_sync': self.config.get('bastion_mode.sync', True)
          }
      # Gather variables from commandline for interpolation
      cli_vars = {}
      # List-type variables
      list_vars = []
      for key, value in kwargs.items():
          if key.startswith('_'):
              cli_vars[key] = value
          elif value and key not in internal_functions.keys():
              if isinstance(value, list) or isinstance(value, tuple):
                  list_vars.append('{k}=$(cat <<EOF\n{v}\nEOF\n)'.format(
                      k=key, v='\n'.join(value)))
              else:
                  cli_vars[key] = value
      # Gather default variables
      vars_list = []
      kwargs_list = [(k,v) for k,v in kwargs.items() if v]
      kwargs_dict_filtered = dict([(k,v) for k,v in kwargs.items() if v])
      # Define the list of yaml variables, excluding the 'inventory' variable (if applicable)
      yaml_variables = [(key,value) for key,value in taskfile_vars.items() if not isinstance(value, dict)]
      # Define the list of default variables,
      # ensuring we only keep those that were
      # not overridden via cli option

      # if var[0] not in [d[0] for d in kwargs_list] and not self.skip_vars_pattern.search(var[1]):

      # Short-circuit the task runner
      # if we're calling functions from the commandline
      cli_functions = ['{k} {v}'.format(
          k=key, v='' if value in [True, False] else value) for key, value in kwargs.items() if
                       value and key in internal_functions.keys()]
      provider_vars = {}
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
      AttrDict.merge(provider_vars, kwargs)
      AttrDict.merge(provider_vars, yaml_variables_wo_jinja)
      # Add the k,v for __tasks_file__
      provider_vars['__tasks_file__'] = self.tf_path
      # Add the k,v for __command__
      provider_vars['__command__'] = command_name
      for k, v in provider_vars.items():
          if isinstance(v, list):
              _v = '\n'.join(v)
              try:
                  provider_vars[k] = f"$(cat <<EOF\n{_v}\nEOF\n)"
              except TypeError as e:
                  if logger.level == 10:
                    logger.error(f"Unsupported variable type, skipped variable {k}")
                    logger.error(f"Skip Reason {e}")
      extra_vars_cli_string = ''.join(f'-e @{e} ' for e in extra_vars)
      extra_vars_string = f'\nextra_vars="{extra_vars_cli_string}"'
      provider_vars_string_block = '\n'.join([f'{k}={v}' for k, v in provider_vars.items()]) + extra_vars_string
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
              cli_vars=cli_vars,
              debug=self.debug,
              extra_vars=extra_vars_cli_string,
              invocation=self.cli_invocation,
              prefix=prefix,
              provider_vars=provider_vars,
              provider_vars_string_block=provider_vars_string_block,
              raw_args=self.raw_args,
              shell_functions=shell_functions,
              suppress_output=self.suppress_output,
              yaml_input_file=self.tf_path
          )
          # Invoke the cli provider
    func.__name__ = function_ref
    return func

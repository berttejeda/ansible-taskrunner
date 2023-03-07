import click
import logging
import sys

from ansible_taskrunner.libs.formatting import logging_format
from ansible_taskrunner.libs.click_extras.help import ExtendedEpilog
from ansible_taskrunner.logger import Logger

logger_obj = Logger()
logger = logger_obj.init_logger('click_commands_cli_entrypoint')

class CLICK_Commands_CLI_Group:

  def create_cli_group(self):

    # Main CLI interface
    click_help_epilog = ""

    @click.group(cls=ExtendedEpilog, help=self.doc, epilog=click_help_epilog,
                 context_settings=dict(max_content_width=self.help_max_content_width))
    @click.version_option(version=self.version)
    @click.option('--config', type=str, nargs=1,
                  help='Specify a config file (default is config.ini)')
    @click.option('--debug', is_flag=True, help='Enable debug output')
    @click.option('--silent', is_flag=True, help='Suppress all output')
    @click.option('--verbose', count=True,
                  help='Increase verbosity of output')
    @click.option('--log', is_flag=True, help='Enable output logging')
    @click.pass_context
    def cli(ctx, **kwargs):
        self.suppress_output = kwargs.get('silent', self.suppress_output)
        # Are we specifying an alternate config file?
        # Verbose mode enabled?
        self.verbose = kwargs.get('verbose', self.verbose)
        # Debug mode enabled?
        self.debug = kwargs.get('debug', self.debug)
        # Set up logging with our desired output level
        if self.debug:
            loglevel = logging.DEBUG  # 10
        elif self.verbose:
            loglevel = logging.INFO  # 20
        else:
            loglevel = logging.INFO  # 20
        logger.setLevel(loglevel)
        if self.suppress_output:
            if sys.version_info[0] >= 3:
                logging.disable(sys.maxsize) # Python 3
            else:
                logging.disable(sys.maxint) # Python 2
        config = kwargs.get('config')
        if config:
            self.config = self.app_config.initialize(config_file=self.config_file)
        else:
            logger.debug(f'No valid config file found {self.config_file}')
            logger.debug('Using program defaults')
        # Add the log  file handler to the logger, if applicable
        if kwargs.get('log') and not self.log_file:
            logger.warning(f'Logging enabled, but no log_file specified in {self.config_file}')
        if kwargs.get('log') and self.log_file:
            filehandler = logging.handlers.RotatingFileHandler(
                self.log_file, maxBytes=self.logging_maxBytes, backupCount=self.logging_backupCount)
            formatter = logging.Formatter(logging_format)
            filehandler.setFormatter(formatter)
            logger.addHandler(filehandler)
        logger.debug('Debug Mode Enabled, keeping any generated temp files')
        return

    return cli

# Import builtins
import os
from string import Template

# Import third-party and custom modules
import click
from ansible_taskrunner.libs.bastion_mode import init_bastion_settings
from ansible_taskrunner.libs.help import SAMPLE_CONFIG
from ansible_taskrunner.libs.help import SAMPLE_TASKS_MANIFEST
from ansible_taskrunner.libs.help import SAMPLE_SFTP_CONFIG
from ansible_taskrunner.logger import Logger

logger_obj = Logger()
logger = logger_obj.init_logger(__name__)

class CLICK_Commands_INIT:

  def create_cli_init_command(self, cli):

    init_epilog = f'''
    Examples:
    - Initialize an empty workspace
        tasks init
    - Initialize an empty workspace config with username and remote path
        tasks init -h myhost.example.org -u {self.local_username} -r "/home/{self.local_username}/git/ansible"
    '''

    # Init command
    @cli.command(cls=self.ExtendedHelp, help='Initialize local directory with sample files',
        epilog=init_epilog, context_settings=dict(max_content_width=180))
    @click.version_option(version=self.version)
    @click.option('---show-samples', is_flag=True,
                  help='Only show a sample task manifest, don\'t write it')
    @self.extend_cli.bastion_mode
    def init(**kwargs):
        logger.info('Initializing ...')
        if kwargs.get('_show_samples'):
            logger.info('Displaying sample config')
            print(SAMPLE_CONFIG)
            logger.info('Displaying sample manifest')
            print(SAMPLE_TASKS_MANIFEST)
            logger.info('Displaying sample sftp config')
            print(SAMPLE_SFTP_CONFIG)
        else:
            if not os.path.exists(self.config_file):
                logger.info(
                    'Existing config not found, writing %s' % self.config_file)
                with open(self.config_file, 'w') as f:
                    f.write(SAMPLE_CONFIG)
            else:
                logger.info(
                    'File exists, not writing sample config %s' % self.config_file)
            if not os.path.exists(self.tasks_file):
                logger.info(
                    'Existing manifest not found, writing %s' % self.tasks_file)
                with open(self.tasks_file, 'w') as f:
                    f.write(SAMPLE_TASKS_MANIFEST)
            else:
                logger.info(
                    'File exists, not writing manifest %s' % self.tasks_file)
            settings_vars = init_bastion_settings(kwargs)
            if not os.path.exists(self.sftp_config_file):
                logger.info(
                    'Existing sftp config not found, writing %s' % self.sftp_config_file)
                with open(self.sftp_config_file, 'w') as f:
                    f.write(Template(SAMPLE_SFTP_CONFIG).safe_substitute(**settings_vars))
            else:
                logger.info(
                    'File exists, not writing sftp config %s' % self.sftp_config_file)


from bertdotconfig import Config
from ansible_taskrunner.defaults import default_settings
from ansible_taskrunner.defaults import default_config_file_name
from ansible_taskrunner.logger import Logger
import os

logger = Logger().init_logger(__name__)

class AppConfig():

  def __init__(self, **kwargs):
    pass

  def initialize(self, **kwargs):

    logger.debug("Initializing config")
    args = kwargs.get('args', {})
    verify_tls = kwargs.get('verify_tls')
    # Initialize App Config
    initial_data = {
    'environment': os.environ
    }  

    config_file_uri = kwargs.get('config_file') or default_config_file_name
    logger.debug(f"Config file URI is {config_file_uri}")
    # Initialize App Config
    config = Config(
        config_file_uri=config_file_uri,
        default_value=default_settings,
        initial_data=initial_data,
        args=args,
        verify_tls=verify_tls
    )

    settings = config.read()

    return settings
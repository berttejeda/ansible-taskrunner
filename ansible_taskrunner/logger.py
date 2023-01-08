import logging
import logging.handlers
import coloredlogs
import os
import sys

class Logger:

  def __init__(self, **kwargs):
    env_debug_is_on = os.environ.get('WEBTERMINAL_DEBUG', '').lower() in [
    't', 'true', '1', 'on', 'y', 'yes']
    self.debug = kwargs.get('debug', False) or env_debug_is_on
    self.FORMAT_STR = "%(asctime)s %(name)s [%(levelname)s]: %(message)s"
    self.formatter = logging.Formatter(
      self.FORMAT_STR,
      datefmt='%Y-%m-%d %H:%M:%S'
    )
    self.logfile_path = kwargs.get('logfile_path')
    self.logfile_write_mode = kwargs.get('logfile_write_mode', 'a')

  def init_logger(self, name=None, debug=False):
    # Setup Logging
    logger = logging.getLogger(name)
    # TODO Find a better approach to this hacky method
    if '--debug' in ' '.join(sys.argv) or self.debug:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
    logger.setLevel(logging_level)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(self.formatter)
    logger.addHandler(stdout_handler)
    if self.logfile_path:
        # create one handler for print and one for export
        file_handler = logging.FileHandler(self.logfile_path, self.logfile_write_mode)
        file_handler.setFormatter(self.formatter)
        logger.addHandler(file_handler)
    coloredlogs.install(logger=logger,
                        fmt=self.FORMAT_STR,
                        level=logging_level)
    return logger
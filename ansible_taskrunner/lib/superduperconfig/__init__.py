import logging
import os
import sys
import yaml

# Logging
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)


class SuperDuperConfig():

    def __init__(self, prog_name):
        self.program_name = prog_name
        self.logger = logger
        pass

    def load_config(self, config_file, req_keys=[], failfast=False, data_key=None, debug=False):
        """ Load config file
        """
        config_path_strings = [
            os.path.realpath(os.path.expanduser(
                os.path.join('~', '.%s' % self.program_name))),
            '.', '/etc/%s' % self.program_name
        ]
        config_paths = [os.path.join(p, config_file)
                        for p in config_path_strings]
        config_found = False
        config_is_valid = False
        for config_path in config_paths:
            config_exists = os.path.exists(config_path)
            if config_exists:
                config_found = True
                try:
                    with open(config_path, 'r') as ymlfile:
                        cfg = yaml.load(ymlfile, yaml.Loader)
                    config_dict = cfg[data_key] if data_key is not None else cfg
                    config_is_valid = all([m[m.keys()[0]].get(k)
                                           for k in req_keys for m in config_dict])
                    self.logger.info(
                        "Found input file - {cf}".format(cf=config_path))
                    if not config_is_valid:
                        logger.warning(
                            """At least one required key was not defined in your input file: {cf}.""".format(
                                cf=config_path)
                        )
                        self.logger.warning(
                            "Review the available documentation or consult --help")
                    config_file = config_path
                    break
                except Exception as e:
                    self.logger.warning(
                        "I encountered a problem reading your input file: {cp}, error was {err}".format(
                            cp=config_path, err=str(e))
                    )
        if not config_found:
            if failfast:
                self.logger.error("Could not find %s. Aborting." % config_file)
                sys.exit(1)
            else:
                self.logger.warning(
                    "Could not find %s, not loading values" % config_file)

        if config_found and config_is_valid:
            return config_dict
        else:
            if failfast:
                self.logger.error(
                    "Config %s is invalid. Aborting." % config_file)
                sys.exit(1)
            else:
                return {}

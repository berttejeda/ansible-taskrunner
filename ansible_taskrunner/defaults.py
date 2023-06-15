default_config_file_name = 'tasks.yaml'
help_max_content_width = 200
logging_maxBytes = 10000000
logging_backupCount = 5
__debug = False
__verbose = 0
suppress_output = 0
log_file = None
path_string = 'vars'

bool_strings_truthy = [
    'true',
    'enabled',
    'on',
    '1',
    'yes',
    'y'
]

bool_strings_false = [
    'false',
    'f',
    'disabled',
    'off',
    '0',
    ]

bool_strings = bool_strings_truthy + bool_strings_false

default_settings = {
  "help": {
    "max_content_width": help_max_content_width,
  },
  "logging": {
    "maxBytes": logging_maxBytes,
    "backupCount": logging_backupCount,
    "debug": __debug,
    "verbose": __verbose,
    "silent": suppress_output,
    "log_file": log_file,
  },
  "taskfile": {
    "path_string": path_string
  }
}

shell_invocation_mappings = {
    'bash': '{src}',
    'python': 'python -c """{src}"""',
    'ruby': 'ruby < <(echo -e """{src}""")'
}

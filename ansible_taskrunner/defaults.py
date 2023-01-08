default_config_file_name = 'tasks.yaml'
help_max_content_width = 200
logging_maxBytes = 10000000
logging_backupCount = 5
__debug = False
__verbose = 0
suppress_output = 0
log_file = None
path_string = 'vars'

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
# Import builtins
import os
import sys

if getattr(sys, 'frozen', False):
    # frozen
    self_file_name = os.path.basename(sys.executable)
else:
    self_file_name = os.path.basename(__file__)
    
# Import third-party and custom modules
try:
    from libs.superduperconfig import SuperDuperConfig
except ImportError as e:
    print('Error in %s ' % os.path.basename(self_file_name))
    print('Failed to import at least one required module')
    print('Error was %s' % e)
    print('Please install/update the required modules:')
    print('pip install -U -r requirements.txt')
    sys.exit(1)


def get_strings():
    self_path = os.path.dirname(os.path.abspath(self_file_name))
    __program_name__ = 'tasks'
    superconf = SuperDuperConfig(__program_name__)
    language_file = '%s/en.yaml' % self_path
    return superconf.load_config(language_file)

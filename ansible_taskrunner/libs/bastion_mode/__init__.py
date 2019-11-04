import getpass
import logging
import os
import sys

local_username = getpass.getuser()

# Setup Logging
logger = logging.getLogger(__name__)
if '--debug run' in ' '.join(sys.argv):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

def init_bastion_settings(kwargs):
	bastion_remote_path = kwargs.get('_bastion_remote_path')
	bastion_host = kwargs.get('_bastion_host')
	bastion_host_port = kwargs.get('_bastion_host_port') or '22'
	bastion_user = kwargs.get('_bastion_user') or local_username
	bastion_ssh_key_file = kwargs.get('_bastion_ssh_key_file')
	if not bastion_remote_path:
	    cur_dir = os.path.basename(os.getcwd())
	    bastion_remote_path = '/home/{}/ansible-taskrunner/{}'.format(bastion_user, cur_dir)
	if not bastion_ssh_key_file:
	    home_dir = os.path.expanduser('~')
	    bastion_ssh_key_file = os.path.join(home_dir, '.ssh', 'id_rsa')
	if not os.path.exists(bastion_ssh_key_file):
	    logger.error("SSH key '%s' not found, specify/generate a new/different key" % bastion_ssh_key_file)
	    sys.exit(1)
	settings = {
	    'bastion_remote_path': bastion_remote_path,
	    'bastion_host': bastion_host,
	    'bastion_host_port': bastion_host_port,
	    'bastion_user': bastion_user,
	    'bastion_ssh_key_file': bastion_ssh_key_file.replace('\\', '\\\\')
	}
	return settings
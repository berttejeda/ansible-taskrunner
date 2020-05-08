import logging
import os
import re
import select
import sys
import zipfile
import warnings


# Setup Logging
logger = logging.getLogger(__name__)
if '--debug run' in ' '.join(sys.argv):
    logger.setLevel(logging.DEBUG)
else:
    # Ignore warnings from cryptography module
    warnings.filterwarnings("ignore", category=UserWarning, module='cryptography')
    warnings.filterwarnings("ignore", category=UserWarning, module='paramiko')
    logger.setLevel(logging.INFO)

# Account for script packaged as an exe via cx_freeze
if getattr(sys, 'frozen', False):
    self_file_name = os.path.basename(sys.executable)
    tasks_file_path = os.path.abspath(sys.executable)
else:
    # Account for script packaged as zip app
    self_file_name = os.path.basename(__file__)
    _tasks_file_path = re.split('.tasks.', os.path.abspath(__file__))[0]
    tasks_file_path = os.path.join(_tasks_file_path, 'tasks')

# Only if zipapp
# Extract any dynamic modules/libraries (aka DLLs)
is_zip = True if zipfile.is_zipfile(tasks_file_path) else False
# For troubleshooting
logger.debug('{} is Zip: {}'.format(tasks_file_path, is_zip))

if is_zip:
    pyver = "py_%s" % '.'.join(['%s' % s for s in sys.version_info[0:3]])
    user_profile = os.environ['USERPROFILE']
    dll_cache_path = '{}\\{}'.format(user_profile, ".ansible_taskrunner")
    dll_sys_path = os.path.join(dll_cache_path, 'libs', pyver)    
    logger.info('Checking for dll sys path %s' % dll_sys_path)
    if not os.path.exists(dll_sys_path):
        if not os.path.exists(dll_cache_path):
            os.makedirs(dll_cache_path)
        logger.info('Dll sys path not found, extracting libraries to %s ...' % dll_cache_path)
        f = zipfile.ZipFile(tasks_file_path,'r')
        dirs = '|'.join(set([re.split('%s.' % pyver,z)[-1].split('/')[0] for z in f.namelist() if re.search("%s/.*pyd$" % pyver, z)]))
        dll_pattern = re.compile(dirs)
        for dll in f.namelist():
            if dll_pattern.search(dll):
                f.extract(dll, dll_cache_path)
        logger.info('Done!')
    sys.path.insert(0, dll_sys_path)    


# Import third-party and custom modules
try:
    import paramiko
    from paramiko import SSHClient, SFTPClient, ssh_exception            
    from socket import gaierror
    import libs.sshutil.scp
    from libs.sshutil.sync import SSHSync
    from libs.sshutil.scp import SCPClient, SCPException        
    from libs.formatting import ansi_colors, Struct
except ImportError as e:
    print('Error in %s ' % os.path.basename(self_file_name))
    print('Failed to import at least one required module')
    print('Error was %s' % e)
    print('Please install/update the required modules:')
    print('pip install -U -r requirements.txt')
    sys.exit(1)

# Make paramiko less verbose
# Only show us warnings if we're not debugging
if '--debug run' not in ' '.join(sys.argv):
    paramiko_logger = logging.getLogger('paramiko')
    paramiko_logger.setLevel(30)

class SSHUtilClient:

    def __init__(self, settings):

        self.settings = settings
        logger.debug("Initializing SSH client ...")
        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.load_system_host_keys()
        logger.info("Connecting to remote host ...")
        try:
            self.ssh.connect(self.settings.host, timeout=10, username=self.settings.user)
        except gaierror as e:
            logger.error(
                "{err}, make sure you have connectivity to {h}".format(
                h=self.settings.host,
                err=e
                )
                )
            sys.exit(1)        
        logger.info("Successfully connected to remote.")
        logger.info("Successfully initialized SSH client.")
    
    # Define scp-put progress callback that prints the current percentage completed for the file
    def progress(self, filename, size, sent):
        sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size)*100) )
    
    def sync(self):
        """pointer to scp module's sync function
        """        
        scp = SCPClient(self.ssh.get_transport(), progress = self.progress)
        sftp = self.ssh.open_sftp()
        sync = SSHSync(scp, sftp)
        logger.info("Successfully initialized SCP client.")        
        return sync

    def execute(self, remote_cmd, stream_stdout=False):
        # Send the command (non-blocking)
        logger.debug("Remote command is '{}'".format(remote_cmd.rstrip('\n')))
        logger.info("Executing command on remote machine...")        
        stdin, stdout, stderr = self.ssh.exec_command(remote_cmd)
        if stream_stdout:
            # Wait for the command to terminate
            while not stdout.channel.exit_status_ready():
                # Only print(data if there is data to read in the channel)
                if stdout.channel.recv_ready():
                    rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
                    if len(rl) > 0:
                        # print(data from stdout)
                        line = stdout.channel.recv(2048).decode("utf-8")
                        print(line)
            # Disconnect from the host
            logger.info("Remote command done, closing SSH connection")
            self.ssh.close()
            return (stdin,stdout,stderr)
        else:
            return (stdin,stdout,stderr)
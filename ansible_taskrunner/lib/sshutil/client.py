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

# Only if zipapp
# Extract any dynamic modules/libraries (aka DLLs)
is_zip = True if zipfile.is_zipfile('tasks') else False
if is_zip:
    pyver = "py%s" % sys.version_info[0]
    dll_cache_path = os.path.expanduser("~/.ansible_taskrunner")
    dll_sys_path = os.path.join(dll_cache_path, 'lib/%s' % pyver)
    logger.info('Checking for dll cache path')
    if not os.path.exists(dll_cache_path):
        logger.info('Dll cache path not found, extracting libraries to %s ...' % dll_cache_path)
        f = zipfile.ZipFile('tasks','r')
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
    from paramiko import SSHClient, ssh_exception            
    from socket import gaierror
    import sshutil.scp
    from sshutil.sync import SSHSync
    from sshutil.scp import SCPClient, SCPException        
    from formatting import ansi_colors, Struct
except ImportError as e:
    print('Error in %s ' % os.path.basename(__file__))
    print('Failed to import at least one required module')
    print('Error was %s' % e)
    print('Please install/update the required modules:')
    print('pip install -U -r requirements.txt')
    sys.exit(1)

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
    
    def sync(self):
        """pointer to scp module's sync function
        """        
        scp = SCPClient(self.ssh.get_transport())
        sync = SSHSync(scp)
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
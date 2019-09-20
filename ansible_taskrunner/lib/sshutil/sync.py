import logging
import os
import sys

# Setup Logging
logger = logging.getLogger(__name__)
if '--debug run' in ' '.join(sys.argv):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# Import third-party and custom modules
try:
    import paramiko
    from paramiko import SSHClient, ssh_exception
except ImportError as e:
    print('Error in %s ' % os.path.basename(__file__))
    print('Failed to import at least one required module')
    print('Error was %s' % e)
    print('Please install/update the required modules:')
    print('pip install -U -r requirements.txt')
    sys.exit(1)

class SSHSync:

    def __init__(self, scp_obj):
        self.scp = scp_obj
        pass

    def to_remote(self, local_path, remote_path):
        logger.debug("Lcl Sync Target {}".format(local_path))
        logger.debug("Rmt Sync Target {}".format(remote_path))
        if os.path.exists(local_path):
            self.scp.put(local_path, remote_path=remote_path, preserve_times=True, recursive=True)
            logger.debug("Successfully copied to remote.")
        else:
            logger.warning("Skipping %s as it does not exist" % local_path.strip())
        return

    def from_remote(self, local_path, remote_path):
        scp.get(remote_path, local_path=local_path, preserve_times=True, recursive=True)
        return

    def get_mod_times(self, dir_path):
        times = {}

        for dirname, subdirnames, filenames in os.walk(dir_path):
            for filename in filenames:
                path = os.path.join(dirname, filename)
                mod_time = os.path.getmtime(path)

                times[path] = mod_time

        return times

    def _get_pkey(self, key):
        '''Get the binary form of the private key
        from the text form
        '''
        if isinstance(key, str):
            key = io.StringIO(key)
        errors = []
        for key_class in (paramiko.rsakey.RSAKey, paramiko.dsskey.DSSKey):
            try:
                return key_class.from_private_key(key)
            except paramiko.SSHException as exc:
                errors.append(exc)
        raise SSHError('Invalid pkey: %s' % (errors))
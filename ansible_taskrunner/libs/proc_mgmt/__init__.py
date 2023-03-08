import logging
import os
import colorama
from subprocess import check_call
import sys
import threading
import time
from ansible_taskrunner.libs.formatting import Struct

# Setup Logging
logger = logging.getLogger(__name__)
if '--debug run' in ' '.join(sys.argv):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


class Remote_CLIInvocation:

    def __init__(self, settings, client):

        self.settings = settings
        self.ssh = client

    def call(self, dirname, cmd, stdout_listen=False):

        base_cmd = "\ncd {};\n".format(dirname.replace('\\', '/'))
        remote_cmd = base_cmd + cmd
        if stdout_listen:
            stdin, stdout, stderr = self.ssh.execute(
                remote_cmd,
                stream_stdout=stdout_listen
            )
            exit_code = stdout.channel.recv_exit_status()
            cli_result = {
                'stdout': [l.strip() for l in stdout],
                'stderr': [l.strip() for l in stderr],
                'returncode': exit_code
            }
            return Struct(**cli_result)
        else:
            stdin, stdout, stderr = self.ssh.execute(remote_cmd)
            exit_code = stdout.channel.recv_exit_status()
            stdout = stdout.readlines() or "None"
            stderr = stderr.readlines() or "None"
            if exit_code == 0:
                return [l.strip() for l in stdout]
            else:
                logger.error('Remote command failed with error {}: {}'.format(exit_code, stderr))
                return False


class CLIInvocation:

    def __init__(self):

        self.proc = None
        self.done = False
        self.invocation = type('obj', (object,), {
            'stdout': None,
            'failed': False,
            'returncode': 0
        }
                               )

    def which(self, program):
        """
        Returns the fully-qualified path to the specified binary
        """

        def is_exe(filepath):
            if sys.platform == 'win32':
                filepath = filepath.replace('\\', '/')
                for exe in [filepath, filepath + '.exe']:
                    if all([os.path.isfile(exe), os.access(exe, os.X_OK)]):
                        return True
            else:
                return os.path.isfile(filepath) and os.access(filepath, os.X_OK)

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file
        return None

    def call(self, cmd, exe='bash', debug_enabled=False, suppress_output=False):

        colorama.init(convert=True, autoreset=True)  # Needed for Windows, supposedly ignored by linux

        executable = self.which(exe)

        if debug_enabled:
            process_invocation = [executable, '-x', '-c', cmd]
        else:
            process_invocation = [executable, '-c', cmd]

        self.invocation.returncode = 0

        try:
            check_call(process_invocation)
        except Exception as e:
            self.invocation.returncode = e.returncode

        return self.invocation

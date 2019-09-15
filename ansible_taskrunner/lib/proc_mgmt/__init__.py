import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import sys
import threading
import time

# Define how we handle different shell invocations
shell_invocation_mappings = { 
    'bash': '{src}',
    'python': 'python -c """{src}"""',
    'ruby': 'ruby < <(echo -e """{src}""")'
}


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

    @staticmethod
    def which(program):
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

    def call(self, cmd, exe='bash', debug_enabled=False):    

        executable = self.which(exe)
        if debug_enabled:
            process_invocation = [executable,'-x','-c', cmd]
        else:
            process_invocation = [executable, '-c', cmd]        

        def s():
            try:
                if sys.version_info[0] >= 3:
                    with Popen(process_invocation, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as self.proc:
                        for line in self.proc.stdout:
                            sys.stdout.write(line)  # process line here
                        if self.proc.returncode != 0:
                            self.invocation.failed = True
                            self.invocation.returncode = p.returncode
                            self.invocation.stdout = 'Encountered error code {errcode} in the specified command {args}'.format(
                                errcode=p.returncode, args=p.args)
                            return self.invocation
                else:
                    # Invoke process
                    self.proc = Popen(
                        process_invocation,
                        stdout=PIPE,
                        stderr=STDOUT)
                    # Poll for new output until finished
                    while True:
                        nextline = self.proc.stdout.readline()
                        if nextline == '' and self.proc.poll() is not None:
                            break
                        sys.stdout.write(nextline)
                        sys.stdout.flush()
                    self.done = True
            except Exception:
                self.done = True
            self.done = True

        try:
            if sys.version_info[0] >= 3:
                t = threading.Thread(target=s, daemon=True)
            else:
                t = threading.Thread(target=s)
            t.start()
        except Exception:
            pass
        try:
            while not self.done:
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            try:
                self.proc.terminate()
            except Exception:
                pass

import os
import sys
from subprocess import PIPE, Popen, STDOUT

# Define how we handle different shell invocations
shell_invocation_mappings = { 
    'bash': '{src}',
    'python': 'python -c """{src}"""',
    'ruby': 'ruby < <(echo -e """{src}""")'
}

class CLIInvocation:

    def __init__(self):
        self.invocation = type('obj', (object,),
                               {
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

    def call(self, cmd, exe='bash'):
        """Call specified command using subprocess library"""
        executable = self.which(exe)
        # Execute the command, catching failures
        try:
            if sys.version_info[0] >= 3:
                # Invoke process and poll for new output until finished
                with Popen([executable, '-c', cmd], stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p:
                    for line in p.stdout:
                        sys.stdout.write(line)  # process line here
                    if p.returncode != 0:
                        self.invocation.failed = True
                        self.invocation.returncode = p.returncode
                        self.invocation.stdout = 'Encountered error code {errcode} in the specified command {args}'.format(
                            errcode=p.returncode, args=p.args)
                        return self.invocation
            else:
                # Invoke process
                process = Popen(
                    [executable, '-c', cmd],
                    stdout=PIPE,
                    stderr=STDOUT)
                # Poll for new output until finished
                while True:
                    nextline = process.stdout.readline()
                    if nextline == '' and process.poll() is not None:
                        break
                    sys.stdout.write(nextline)
                    sys.stdout.flush()
        except Exception as e:
            print(
                'Encountered error in the specified command, error was {err}'.format(err=e))

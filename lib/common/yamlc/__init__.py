import platform
import os
import re
import sys
from subprocess import PIPE, Popen, STDOUT

class YamlCLIInvocation:

    def __init__(self, **kwargs):
        self.invocation = type('obj', (object,),
            {
            'stdout' : None,
            'failed' : False,
            'returncode' : 0
            }
            )

    def get_distribution(self):
        """Return the OS distribution name"""
        if platform.system() == 'Linux':
            try:
                supported_dists = platform._supported_dists + ('arch', 'alpine', 'devuan')
                distribution = platform.linux_distribution(supported_dists=supported_dists)[0].capitalize()
                if not distribution and os.path.isfile('/etc/system-release'):
                    distribution = platform.linux_distribution(supported_dists=['system'])[0].capitalize()
                    if 'Amazon' in distribution:
                        distribution = 'Amazon'
                    else:
                        distribution = 'OtherLinux'
            except:
                distribution = sys.platform.dist()[0].capitalize()
        else:
            distribution = None
        return distribution

    def which(self, program):
        '''
        Returns the fully-qualified path to the specified binary
        '''
        def is_exe(fpath):
            if sys.platform == 'win32':
                fpath = fpath.replace('\\','/')
                for exe in [fpath, fpath + '.exe']:
                    if all([os.path.isfile(exe), os.access(exe, os.X_OK)]):
                        return True
            else:
                return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
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

    def call(self, cmd):
        """Call specified command using subprocess library"""
        bash_binary = self.which('bash')
        # Execute the command, catching failures
        if self.get_distribution() == 'Ubuntu':
          bash_cmd = [bash_binary, '-l']
        else:
          bash_cmd = [bash_binary]
        try:
          if sys.version_info[0] >= 3:
              # Invoke process and poll for new output until finished
              with Popen( [bash_binary, '-c', cmd], stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p:
                for line in p.stdout:
                    sys.stdout.write(line) # process line here
                if p.returncode != 0:
                    self.invocation.failed = True
                    self.invocation.returncode = p.returncode
                    self.invocation.stdout = 'Encountered error code {errcode} in the specified command {args}'.format(errcode=p.returncode, args=p.args)
                    return self.invocation                    
          else:
              # Invoke process
              process = Popen(
                [bash_binary, '-c', cmd], 
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
            print('Encountered error in the specified command, error was {err}'.format(err=e))

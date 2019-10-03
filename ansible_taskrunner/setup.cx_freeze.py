import cx_Freeze
from cx_Freeze import setup
from cx_Freeze import Executable
import os
import sys

# cx_Freeze is a set of scripts and modules for freezing Python scripts
# into executables in much the same way that py2exe and py2app do. 
# Unlike these two tools, cx_Freeze is cross platform and should work on any 
# platform that Python itself works on. 
# It requires Python 2.7 or higher and does work with Python 3.

# Set the TCL and TK library paths if your script utilizes tkinter for GUI programming
# Adjust path to match the location of the tcl8.6 and tk8.6 library directories
# os.environ['TCL_LIBRARY'] = r'C:\\somepath\\lib\\tcl8.6'
# os.environ['TK_LIBRARY'] = r'C:\\somepath\\lib\\tk8.6'


buildOptions = dict(
    include_msvcr=True,
    # Any packages that need to be added for compilation.
    # Some may work but if not include them here
    packages=[],
    includes=['_cffi_backend','paramiko', 'cryptography']
)

setup(
    name="ansible-taskrunner",
    version = "1.1.10",
    author="Engelbert Tejeda",
    description="ansible-playbook wrapper with YAML-abstracted python click cli options",
    license="MIT License",
    options=dict(build_exe=buildOptions),
    executables=[Executable("cli.py",
                            base=None,
                            targetName="tasks.exe",
                            )],
)


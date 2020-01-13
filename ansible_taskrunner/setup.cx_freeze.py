import cx_Freeze
from cx_Freeze import setup
from cx_Freeze import Executable
import msilib
import io
import os
import re
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

# Include support files
include_files = [
'build/README.html',
'files/start-tutorial.bat',
'files/tasks-console.bat',
'files/cfg',
'files/macros'
]

buildOptions = dict(
    include_msvcr=True,
    # Any packages that need to be added for compilation.
    # Some may work, but if not, include them here
    packages=[],
    includes=['_cffi_backend','paramiko', 'cryptography'],
    include_files=include_files
)

with io.open('cli.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

UPGRADE_CODE = '{18b8211b-8cea-4f5c-ab88-6149721c5fb3}'
PRODUCT_CODE = msilib.gen_uuid()
COMPANY_NAME = 'etejeda'

directory_table = [
    (
        'StartMenuFolder',
        'TARGETDIR',
        '.',
    ),
    (
        'MyProgramMenu',
        'StartMenuFolder',
        'ANSIBL~1|Ansible Taskrunner',
    ),
]

# http://msdn.microsoft.com/en-us/library/windows/desktop/aa371847(v=vs.85).aspx
shortcut_table = [
    ("DesktopShortcut",             # Shortcut
     "DesktopFolder",               # Directory_
     "Ansible Taskrunner Console",  # Name
     "TARGETDIR",                   # Component_
     "[TARGETDIR]\\tasks-console.bat",      # Target
     None,                          # Arguments
     None,                          # Description
     None,                          # Hotkey
     None,                          # Icon
     None,                          # IconIndex
     None,                          # ShowCmd
     'TARGETDIR'                    # WkDir
     ),
    (
    'ProgramShortcut',        # Shortcut
    'MyProgramMenu',          # Directory_
    'Ansible Taskrunner %s' % version,  # Name
    'TARGETDIR',              # Component_
    '[TARGETDIR]tasks-console.bat',# Target
    None,                     # Arguments
    None,                     # Description
    None,                     # Hotkey
    None,                     # Icon
    None,                     # IconIndex
    None,                     # ShowCmd
    # PersonalFolder is My Documents, use as Start In folder
    'PersonalFolder'          # WkDir
    ),
    (
    'DocShortcut',            # Shortcut
    'MyProgramMenu',          # Directory_
    'Documentation',          # Name
    'TARGETDIR',              # Component_
    '[TARGETDIR]README.html',# Target
    None,                     # Arguments
    None,                     # Description
    None,                     # Hotkey
    None,                     # Icon
    None,                     # IconIndex
    None,                     # ShowCmd
    'TARGETDIR'               # WkDir
    ),
    (
    'UninstallShortcut',      # Shortcut
    'MyProgramMenu',          # Directory_
    'Uninstall',              # Name
    'TARGETDIR',              # Component_
    '[SystemFolder]msiexec.exe', # Target
    '/x %s' % PRODUCT_CODE,           # Arguments
    None,                     # Description
    None,                     # Hotkey
    None,                     # Icon
    None,                     # IconIndex
    None,                     # ShowCmd
    # PersonalFolder is My Documents, use as Start In folder
    'TARGETDIR'               # WkDir
    ), 
    ]

# Now create the table dictionary
msi_data = {
'Directory': directory_table,
"Shortcut": shortcut_table,
# 'Icon': [('Ansible-Icon', msilib.Binary('resources/ansible-taskrunner.ico')),],
# 'Property': [('ARPPRODUCTICON', 'ANSIBLE-TASKRUNNER-Icon'),]
}

# Change some default MSI options and specify the use of the above defined tables
bdist_msi_options = {
'data': msi_data,
'add_to_path': True,
'upgrade_code': UPGRADE_CODE,
'product_code': PRODUCT_CODE,
'initial_target_dir': r'[ProgramFilesFolder]\\%s' % ('ansible-taskrunner'),
}

setup(
    name="ansible-taskrunner %s" % version,
    version = version,
    author="Engelbert Tejeda",
    description="ansible-playbook wrapper with YAML-abstracted python click cli options",
    license="MIT License",
    options=dict(
        build_exe=buildOptions, 
        bdist_msi=bdist_msi_options),
    executables=[Executable(
        "cli.py",
        # Set base=Win32GUI 
        # Only needed if your script utilizes 
        # tkinter for GUI programming
        base=None,
        targetName="tasks.exe",
        copyright="Copyright (C) 2020 %s" % COMPANY_NAME,
        shortcutName = "Ansible Taskrunner"
    )],
)


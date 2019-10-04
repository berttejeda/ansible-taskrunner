# Defaults
ansi_colors = """
RESTORE=$(echo -en '\033[0m')
RED=$(echo -en '\033[00;31m')
GREEN=$(echo -en '\033[00;32m')
YELLOW=$(echo -en '\033[00;33m')
BLUE=$(echo -en '\033[00;34m')
MAGENTA=$(echo -en '\033[00;35m')
PURPLE=$(echo -en '\033[00;35m')
CYAN=$(echo -en '\033[00;36m')
LIGHTGRAY=$(echo -en '\033[00;37m')
"""

logging_format = "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"


def reindent(s, numSpaces):
    """Remove leading spaces from string see: Python Cookbook by David Ascher, Alex Martelli"""
    s = s.split('\n')
    s = [(numSpaces * ' ') + line.lstrip() for line in s]
    s = '\n'.join(s)
    return s


class Struct:
	def __init__(self, **entries):
		self.__dict__.update(entries)

	def get(self, _key):
		return self.__dict__.get(_key)

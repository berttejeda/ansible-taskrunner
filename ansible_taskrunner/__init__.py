import sys

if sys.version_info > (3, 8):
  from importlib import metadata
  __version__ = metadata.version("ansible_taskrunner")
else:
  import importlib_metadata;
  __version__ = importlib_metadata.version('ansible_taskrunner')
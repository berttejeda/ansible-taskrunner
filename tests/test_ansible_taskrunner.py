#!/usr/bin/env python
# coding=utf-8
""" Integration and unit tests for ansible taskrunner
"""
from __future__ import print_function, absolute_import
import os
import sys
import unittest
import warnings
from click.testing import CliRunner

# Globals
__author__ = 'etejeda'

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root + '/ansible_taskrunner')

# Don't create .pyc files for non-modules
sys.dont_write_bytecode = True
import cli as cli_interface

class TestCli(unittest.TestCase):

    def setUp(self):
        self.cli = CliRunner()

    def test_help(self):
        """ Test whether script help will return.  Basically check whether there are compile errors
        :return: exit_code == 0
        """
        self.assertEqual(self.cli.invoke(cli_interface.cli, ['--help']).exit_code, 0)
        pass

    def test_run_help(self):
        """ Test whether script help will return.  Basically check whether there are compile errors
        :return: exit_code == 0
        """
        self.assertEqual(self.cli.invoke(cli_interface.cli, ['run', '--help']).exit_code, 0)
        pass

if __name__ == '__main__':
    with warnings.catch_warnings(record=True):
        unittest.main()

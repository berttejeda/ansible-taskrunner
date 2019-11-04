#!/usr/bin/env python
# coding=utf-8
""" Unit tests for ansible taskrunner
"""
from __future__ import print_function, absolute_import
from click.testing import CliRunner
import os
from subprocess import PIPE, Popen
import sys
import unittest
import warnings

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
        """ Test whether script help will successfully execute.  Basically check whether there are compile errors
        :return: exit_code == 0
        """
        self.assertEqual(self.cli.invoke(cli_interface.cli, ['run', '--help']).exit_code, 0)
        pass

    def test_run_foo_echo(self):
        """ Test whether script 'run' subcommand will successfully echo subcommand.  Basically check whether there are compile errors
        :return: exit_code == 0
        """
        self.assertEqual(self.cli.invoke(cli_interface.cli, ['run', '-f', 'foo', '---echo']).exit_code, 0)
        pass

    def test_run_make_hello(self):
        """ Test whether script 'run' subcommand will successfully execute in make mode.  Basically check whether there are compile errors
        :return: exit_code == 0
        """
        self.assertEqual(self.cli.invoke(cli_interface.cli, ['run', '-f', 'foo', '---make', 'hello']).exit_code, 0)
        pass

    def test_run_make_echo(self):
        """ Test whether script 'run' subcommand will successfully echo subcommand in make mode.  Basically check whether there are compile errors
        :return: exit_code == 0
        """
        self.assertEqual(self.cli.invoke(cli_interface.cli, ['run', '-f', 'foo', '---make', 'hello','---echo']).exit_code, 0)
        pass

    def test_direct_call(self):
        proc = Popen(['python', 'ansible_taskrunner/cli.py', '--help'], stdout=PIPE)
        stdout, stderr = proc.communicate()
        self.assertTrue(stdout.startswith(b'Usage:'))
        self.assertEquals(0, proc.returncode)        


if __name__ == '__main__':
    with warnings.catch_warnings(record=True):
        unittest.main()

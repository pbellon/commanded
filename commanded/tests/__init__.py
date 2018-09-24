import unittest
import sys
import argparse
from os import path
from unittest.mock import patch
from commanded import with_commands, command, command_arg
import io

@with_commands(description='Fake api test', prog='fake')
class FakeApi:
    factor = 3

    @command(name='do', args=(command_arg('a', nargs=1, type=int)))
    def do_stuff(self, a=[1]):
        return a[0] * self.factor

    @command(name='other', args=(command_arg('-n', '--name', type=str),))
    def get_name(self, name):
        return "My name is %s" % name

    @command(name='read', args=(
        command_arg('-f', '--file', type=argparse.FileType('r')),
    ))
    def read(self, file):
        return ("".join(file)).strip()

class TestCommandedApi(unittest.TestCase):
    def setUp(self):
        test_dir = path.dirname(path.realpath(__file__))
        self.api = FakeApi()
        self.file_path = path.join(test_dir, 'infile.txt')
        self.file = io.open(self.file_path, 'r')
        self.file_content = self.file.read()

    def tearDown(self):
        self.file.close()

    def test_parse_args(self):
        with patch.object(sys, 'argv', ['fake', 'do', '3']):
            result = self.api.parse_args()
            self.assertEqual(result, 9)

        with patch.object(sys, 'argv', ['fake', 'other', '--name', 'test']):
            result = self.api.parse_args()
            self.assertEqual(result, "My name is test")

        with patch.object(sys, 'argv', ['fake', 'read', '--file', self.file_path ]):
            result = self.api.parse_args()
            self.assertEqual(result, "iz win")

    def test_list_bindings(self):
        bindings = self.api.list_bindings()
        nbCommands = len(bindings.keys())
        self.assertEqual(nbCommands, 3)

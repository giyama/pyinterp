from __future__ import absolute_import
from __future__ import print_function

import subprocess

from distutils.command.build import build as _build

import setuptools
# test1 test echo
CUSTOM_COMMANDS = [['apt-get', 'update'],
    ['apt-get', '--assume-yes', 'install', 'unzip'],
    ['apt-get', '--assume-yes', 'install', 'default-jre'],
    ['apt-get', '--assume-yes', 'install', 'perl']]

class CustomCommands(setuptools.Command):
    """A setuptools Command class able to run arbitrary commands."""

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def RunCustomCommand(self, command_list):
        print
        'Running command: %s' % command_list
        p = subprocess.Popen(
            command_list,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # Can use communicate(input='y\n'.encode()) if the command run requires
        # some confirmation.
        stdout_data, _ = p.communicate()
        print
        'Command output: %s' % stdout_data
        if p.returncode != 0:
            raise RuntimeError(
                'Command %s failed: exit code: %s' % (command_list, p.returncode))

    def run(self):
        for command in CUSTOM_COMMANDS:
            self.RunCustomCommand(command)

REQUIRED_PACKAGES = [

]



setuptools.setup(
    name=pyinterp,
    version='0.8.0',
    description='Pre built pyinterp lib',
    install_requires=REQUIRED_PACKAGES,
    packages=setuptools.find_packages(),
    cmdclass={
        'build': build,
        'CustomCommands': CustomCommands,
    }
)

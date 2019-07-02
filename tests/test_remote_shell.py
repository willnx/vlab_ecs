# -*- coding: UTF-8 -*-
"""A suite of unit tests for the ``remote_shell.py`` module"""
import unittest
from unittest.mock import patch, MagicMock

from vlab_ecs_api.lib.worker import remote_shell


class TestSSHClient(unittest.TestCase):
    """"A suite of test cases for the ``SSHClient`` class"""
    def _config_patching(self, fake_SSHClient):
        self.fake_channel = MagicMock()
        self.fake_transport = MagicMock()
        self.fake_transport.open_session.return_value = self.fake_channel
        self.fake_ssh = MagicMock()
        self.fake_ssh.get_transport.return_value = self.fake_transport
        fake_SSHClient.return_value = self.fake_ssh

    @patch.object(remote_shell.paramiko.client, 'SSHClient')
    def test_init_connects(self, fake_SSHClient):
        """``SSHClient`` - Establishes an SSH connection upon object initialization"""
        self._config_patching(fake_SSHClient)
        ssh = remote_shell.SSHClient(hostname='some.server.io',
                                     port=22,
                                     username='pat',
                                     password='iLoveKats!')

        self.assertTrue(self.fake_ssh.connect.called)

    @patch.object(remote_shell.SSHClient, '_block_on_command')
    @patch.object(remote_shell.paramiko.client, 'SSHClient')
    def test_exec_command(self, fake_SSHClient, fake_block_on_command):
        """``SSHClient`` - the 'exec_command' method returns a Tuple of stdout, stderr, and the exit code"""
        self._config_patching(fake_SSHClient)
        fake_block_on_command.return_value = ('stdout', 'stderr', 0)
        ssh = remote_shell.SSHClient(hostname='some.server.io',
                                     port=22,
                                     username='pat',
                                     password='iLoveKats!')

        output = ssh.exec_command('/some/shell/command')
        expected = ('stdout', 'stderr', 0)

        self.assertEqual(output, expected)

    @patch.object(remote_shell.SSHClient, '_block_on_command')
    @patch.object(remote_shell.paramiko.client, 'SSHClient')
    def test_exec_command_blocks(self, fake_SSHClient, fake_block_on_command):
        """``SSHClient`` - the 'exec_command' method blocks until the command completes"""
        self._config_patching(fake_SSHClient)
        fake_block_on_command.return_value = ('stdout', 'stderr', 0)
        ssh = remote_shell.SSHClient(hostname='some.server.io',
                                     port=22,
                                     username='pat',
                                     password='iLoveKats!')

        ssh.exec_command('/some/shell/command')

        self.assertTrue(fake_block_on_command.called)

    @patch.object(remote_shell.SSHClient, '_block_on_command')
    @patch.object(remote_shell.paramiko.client, 'SSHClient')
    def test_exec_command_pty(self, fake_SSHClient, fake_block_on_command):
        """``SSHClient`` - the 'exec_command' method obtains a PTY by default"""
        self._config_patching(fake_SSHClient)
        fake_block_on_command.return_value = ('stdout', 'stderr', 0)
        ssh = remote_shell.SSHClient(hostname='some.server.io',
                                     port=22,
                                     username='pat',
                                     password='iLoveKats!')

        ssh.exec_command('/some/shell/command')

        self.assertTrue(self.fake_channel.get_pty.called)

    def test_block_on_command(self):
        """``SSHClient`` - the '_block_on_command' method blocks until an exit code is ready"""
        fake_channel = MagicMock()
        fake_channel.exit_status_ready.return_value = True
        fake_channel.recv.return_value = b'some output'
        fake_channel.recv_stderr.return_value = b'some stderr output'
        fake_channel.recv_exit_status.return_value = 0

        remote_shell.SSHClient._block_on_command(fake_channel)

        self.assertTrue(fake_channel.exit_status_ready.called)


    def test_block_on_command_reads(self):
        """``SSHClient`` - the '_block_on_command' method reads the stderr and stdout buffers while the command runs"""
        fake_channel = MagicMock()
        fake_channel.exit_status_ready.return_value = True
        fake_channel.recv.return_value = b'some output'
        fake_channel.recv_stderr.return_value = b'some stderr output'
        fake_channel.recv_exit_status.return_value = 0

        remote_shell.SSHClient._block_on_command(fake_channel)

        self.assertTrue(fake_channel.recv.called)
        self.assertTrue(fake_channel.recv_stderr.called)


if __name__ == '__main__':
    unittest.main()

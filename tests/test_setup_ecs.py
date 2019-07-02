# -*- coding: UTF-8 -*-
"""A suite of unit tests for the ``setup_ecs.py`` module"""
import unittest
from unittest.mock import patch, MagicMock

from vlab_ecs_api.lib.worker import setup_ecs


class TestSetupECS(unittest.TestCase):
    """A set of test cases for the ``setup_ecs.py`` module"""

    @classmethod
    def setUp(cls):
        """Runs before every test case"""
        cls.logger = MagicMock()
        cls.ssh_client = MagicMock()
        cls.ssh_client.exec_command.return_value = ('stdout', 'stderr', 0)

    @patch.object(setup_ecs, 'SSHClient')
    @patch.object(setup_ecs, '_accept_license')
    @patch.object(setup_ecs, '_update_ip')
    @patch.object(setup_ecs, '_update_disk')
    @patch.object(setup_ecs, '_update_dns_and_ntp')
    @patch.object(setup_ecs, '_run_update_deploy')
    @patch.object(setup_ecs, '_run_step1')
    @patch.object(setup_ecs, '_run_step2')
    def test_configure(self, fake_run_step2, fake_run_step1, fake_run_update_deploy,
                       fake_update_dns_and_ntp, fake_update_disk, fake_update_ip,
                       fake_accept_license, fake_SSHClient):
        """``configure`` is a simple wrapper to configure *all the things* for ECS"""
        setup_ecs.configure(ssh_port=50022,
                            gateway_ip='10.1.1.1',
                            ecs_ip='192.168.1.56',
                            logger=self.logger)

        self.assertTrue(fake_accept_license.called)
        self.assertTrue(fake_update_ip.called)
        self.assertTrue(fake_update_disk.called)
        self.assertTrue(fake_update_dns_and_ntp.called)
        self.assertTrue(fake_run_update_deploy.called)
        self.assertTrue(fake_run_step1.called)
        self.assertTrue(fake_run_step2.called)

    def test_accept_license(self):
        """``_accept_license`` runs the expected command"""
        config_file = '/some/path/deploy.yml'
        setup_ecs._accept_license(self.ssh_client, config_file, self.logger)

        the_args, _  = self.ssh_client.exec_command.call_args
        cli_cmd = the_args[0]
        expected = "/usr/bin/sed  -i -e 's/license_accepted: false/license_accepted: true/g' /some/path/deploy.yml"

        self.assertEqual(expected, cli_cmd)

    def test_accept_license_error(self):
        """``_accept_license`` raises RuntimeError if the command has a non-zero exit code"""
        self.ssh_client.exec_command.return_value = ('stdout', 'stderr', 1)
        config_file = '/some/path/deploy.yml'
        with self.assertRaises(RuntimeError):
            setup_ecs._accept_license(self.ssh_client, config_file, self.logger)

    def test_update_ip(self):
        """``_update_ip`` runs the expected command"""
        config_file = '/some/path/deploy.yml'
        ecs_ip = '192.168.1.56'
        setup_ecs._update_ip(self.ssh_client, ecs_ip, config_file, self.logger)

        the_args, _  = self.ssh_client.exec_command.call_args
        cli_cmd = the_args[0]
        expected = "/usr/bin/sed  -i -e 's/192.168.2.200/192.168.1.56/g' /some/path/deploy.yml"

        self.assertEqual(expected, cli_cmd)

    def test_update_ip_error(self):
        """``_update_ip`` raises RuntimeError if the command has a non-zero exit code"""
        self.ssh_client.exec_command.return_value = ('stdout', 'stderr', 1)
        config_file = '/some/path/deploy.yml'
        ecs_ip = '192.168.1.56'
        with self.assertRaises(RuntimeError):
            setup_ecs._update_ip(self.ssh_client, ecs_ip, config_file, self.logger)

    def test_update_disk(self):
        """``_update_disk`` runs the expected command"""
        config_file = '/some/path/deploy.yml'
        setup_ecs._update_disk(self.ssh_client, config_file, self.logger)

        the_args, _  = self.ssh_client.exec_command.call_args
        cli_cmd = the_args[0]
        expected = "/usr/bin/sed  -i -e 's/\\/dev\\/vda/\\/dev\\/sdb/g' /some/path/deploy.yml"

        self.assertEqual(expected, cli_cmd)

    def test_update_disk_error(self):
        """``_update_disk`` raises RuntimeError if the command has a non-zero exit code"""
        self.ssh_client.exec_command.return_value = ('stdout', 'stderr', 1)
        config_file = '/some/path/deploy.yml'
        with self.assertRaises(RuntimeError):
            setup_ecs._update_disk(self.ssh_client, config_file, self.logger)

    def test_update_dns_and_ntp(self):
        """``_update_dns_and_ntp`` runs the expected command"""
        config_file = '/some/path/deploy.yml'
        setup_ecs._update_dns_and_ntp(self.ssh_client, config_file, self.logger)

        the_args, _  = self.ssh_client.exec_command.call_args
        cli_cmd = the_args[0]
        expected = "/usr/bin/sed  -i -e 's/192.168.2.2/192.168.1.1/g' /some/path/deploy.yml"
        self.assertEqual(expected, cli_cmd)

    def test_update_dns_and_ntp_error(self):
        """``_update_dns_and_ntp`` raises RuntimeError if the command has a non-zero exit code"""
        self.ssh_client.exec_command.return_value = ('stdout', 'stderr', 1)
        config_file = '/some/path/deploy.yml'
        with self.assertRaises(RuntimeError):
            setup_ecs._update_dns_and_ntp(self.ssh_client, config_file, self.logger)

    def test_run_update_deploy(self):
        """``_run_update_deploy`` runs the expected command"""
        setup_ecs._run_update_deploy(self.ssh_client, self.logger)

        the_args, _  = self.ssh_client.exec_command.call_args
        cli_cmd = the_args[0]
        expected = ". .profile ; /bin/echo ChangeMe | /usr/bin/sudo -Si /usr/bin/date && /home/admin/bin/update_deploy 2>&1 >> /home/admin/auto_config.log"
        self.assertEqual(expected, cli_cmd)

    def test_run_update_deploy_error(self):
        """``_run_update_deploy`` raises RuntimeError if the command has a non-zero exit code"""
        self.ssh_client.exec_command.return_value = ('stdout', 'stderr', 1)
        with self.assertRaises(RuntimeError):
            setup_ecs._run_update_deploy(self.ssh_client, self.logger)

    def test_run_step1(self):
        """``_run_step1`` runs the expected command"""
        setup_ecs._run_step1(self.ssh_client, self.logger)
        the_args, _  = self.ssh_client.exec_command.call_args
        cli_cmd = the_args[0]
        expected = ". .profile ; /bin/echo ChangeMe | /usr/bin/sudo -Si /usr/bin/date && /home/admin/bin/ova-step1 2>&1 >> /home/admin/auto_config.log"
        self.assertEqual(expected, cli_cmd)

    def test_run_step1_error(self):
        """``_run_step1`` raises RuntimeError if the command has a non-zero exit code"""
        self.ssh_client.exec_command.return_value = ('stdout', 'stderr', 1)
        with self.assertRaises(RuntimeError):
            setup_ecs._run_step1(self.ssh_client, self.logger)

    def test_run_step2(self):
        """``_run_step2`` runs the expected command"""
        setup_ecs._run_step2(self.ssh_client, self.logger)
        the_args, _  = self.ssh_client.exec_command.call_args
        cli_cmd = the_args[0]
        expected = ". .profile ; /bin/echo ChangeMe | /usr/bin/sudo -Si /usr/bin/date && /home/admin/bin/ova-step2 2>&1 >> /home/admin/auto_config.log"
        self.assertEqual(expected, cli_cmd)

    def test_run_step2_error(self):
        """``_run_step2`` raises RuntimeError if the command has a non-zero exit code"""
        self.ssh_client.exec_command.return_value = ('stdout', 'stderr', 1)
        with self.assertRaises(RuntimeError):
            setup_ecs._run_step2(self.ssh_client, self.logger)


if __name__ == '__main__':
    unittest.main()

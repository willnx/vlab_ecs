# -*- coding: UTF-8 -*-
"""
Contains logic for bootstrapping a CentOS 7 VM into an ECS appliance.
For whatever reason, ECS requires a TTY (or PTY) to configure. As a workaround,
this module leverages SSH to mimic a user.
"""
import textwrap

from vlab_ecs_api.lib import const
from vlab_ecs_api.lib.worker.remote_shell import SSHClient


CONFIG_FILE = '/home/admin/ECS-CommunityEdition/deploy.yml'
ECS_VM_LOGFILE = '2>&1 >> /home/admin/auto_config.log' # redirects stderr and stdout to a file
SED_COMMAND = '/usr/bin/sed'
# Gross, right? Well ECS devs assume a TTY, and have shitty path management.
# This means if you just "sudo at the start" to avoid the prompt in your
# automation, you'll break the path. So fuck it, just run some bull shit command
# to prime sudo, so when that garbage ECS script calls sudo it wont prompt for
# a password.
# Finally, it's up to the client to read the profile to set some env vars
# if we don't do this, for some reason, starting ntpd hangs...
PRIME_SUDO = '. .profile ; /bin/echo {} | /usr/bin/sudo -Si /usr/bin/date &&'.format(const.VLAB_ECS_ADMIN_PW)


def configure(ssh_port, gateway_ip, ecs_ip, logger):
    """A convenient wrapper function to bootstrap a CentOS 7 VM into an ECS instance.

    :Returns: None

    :param ssh_port: The port on the gateway which forwards SSH to the ECS instance
    :type ssh_port: Integer

    :param gateway_ip: The IP fo the NAT-ing gateway
    :type gateway_ip: String

    :param ecs_ip: The IP (inside the NAT) that the ECS instance should bind to
    :type ecs_ip: String

    :param logger: The task logging object
    :type logger: logging.LoggerAdapter
    """
    logger.info("SSHing into {} via port {}".format(gateway_ip, ssh_port))
    ssh_client = SSHClient(hostname=gateway_ip,
                           port=ssh_port,
                           username=const.VLAB_ECS_ADMIN,
                           password=const.VLAB_ECS_ADMIN_PW)

    logger.info('Updating config: {}'.format(CONFIG_FILE))
    _accept_license(ssh_client, CONFIG_FILE, logger)
    _update_ip(ssh_client, ecs_ip, CONFIG_FILE, logger)
    _update_disk(ssh_client, CONFIG_FILE, logger)
    _update_dns_and_ntp(ssh_client, CONFIG_FILE, logger)
    logger.info('Running update_deploy')
    _run_update_deploy(ssh_client, logger)
    logger.info('Running Step 1')
    _run_step1(ssh_client, logger)
    logger.info('Running Step 2')
    _run_step2(ssh_client, logger)


def _accept_license(ssh_client, config_file, logger):
    """Update the ECS config so it doesn't prompt the automation to accept the EULA

    :Returns: None

    :Raises: RuntimeError

    :param ssh_client: An established ssh connection to the ECS instance
    :type ssh_client: vlab_ecs_api.lib.worker.remote_shell.SSHClient

    :param config_file: The location of the ECS deploy.yml file
    :type config_file: String

    :param logger: The task logging object
    :type logger: logging.LoggerAdapter
    """
    license_string = 'license_accepted: false'
    license_accept = 'license_accepted: true'
    args = " -i -e 's/{}/{}/g' {}".format(license_string, license_accept, config_file)
    command = '{} {}'.format(SED_COMMAND, args)
    stdout, stderr, exit_code = ssh_client.exec_command(command)
    if exit_code:
        message = 'Failed to update config to accept software license'
        logger.error(message)
        logger.error('EC: {}, TYPE: {}'.format(exit_code, type(exit_code)))
        logger.error('\nCMD: {}\nEC: {}\nSTDOUT:{}\nSTDERR:{}'.format(command, exit_code, stdout, stderr))
        raise RuntimeError(message)


def _update_ip(ssh_client, ecs_ip, config_file, logger):
    """Update the ECS config to bind to the external IP of the CentOS VM

    :Returns: None

    :Raises: RuntimeError

    :param ssh_client: An established ssh connection to the ECS instance
    :type ssh_client: vlab_ecs_api.lib.worker.remote_shell.SSHClient

    :param ecs_ip: The IP (inside the NAT) that the ECS instance should bind to
    :type ecs_ip: String

    :param config_file: The location of the ECS deploy.yml file
    :type config_file: String

    :param logger: The task logging object
    :type logger: logging.LoggerAdapter
    """
    default_ecs_ip = '192.168.2.200'
    args = " -i -e 's/{}/{}/g' {}".format(default_ecs_ip, ecs_ip, config_file)
    command = '{} {}'.format(SED_COMMAND, args)
    stdout, stderr, exit_code = ssh_client.exec_command(command)
    if exit_code:
        message = 'Failed to change the default ECS IP in the config'
        logger.error(message)
        logger.error('\nCMD: {}\nEC: {}\nSTDOUT:{}\nSTDERR:{}'.format(command, exit_code, stdout, stderr))
        raise RuntimeError(message)


def _update_disk(ssh_client, config_file, logger):
    """Update the ECS config to use the correct block device for the object store

    :Returns: None

    :Raises: RuntimeError

    :param ssh_client: An established ssh connection to the ECS instance
    :type ssh_client: vlab_ecs_api.lib.worker.remote_shell.SSHClient

    :param config_file: The location of the ECS deploy.yml file
    :type config_file: String

    :param logger: The task logging object
    :type logger: logging.LoggerAdapter
    """
    old_disk = '\/dev\/vda'
    new_disk = '\/dev\/sdb'
    args = " -i -e 's/{}/{}/g' {}".format(old_disk, new_disk, config_file)
    command = '{} {}'.format(SED_COMMAND, args)
    stdout, stderr, exit_code = ssh_client.exec_command(command)
    if exit_code:
        message = 'Failed to update the disk in config file'
        logger.error(message)
        logger.error('\nCMD: {}\nEC: {}\nSTDOUT:{}\nSTDERR:{}'.format(command, exit_code, stdout, stderr))
        raise RuntimeError(message)


def _update_dns_and_ntp(ssh_client, config_file, logger):
    """Update the ECS config to use the user's vLab gateway for DNS and NTP

    :Returns: None

    :Raises: RuntimeError

    :param ssh_client: An established ssh connection to the ECS instance
    :type ssh_client: vlab_ecs_api.lib.worker.remote_shell.SSHClient

    :param config_file: The location of the ECS deploy.yml file
    :type config_file: String

    :param logger: The task logging object
    :type logger: logging.LoggerAdapter
    """
    default_ip = '192.168.2.2'
    new_ip = '192.168.1.1'
    args = " -i -e 's/{}/{}/g' {}".format(default_ip, new_ip, config_file)
    command = '{} {}'.format(SED_COMMAND, args)
    stdout, stderr, exit_code = ssh_client.exec_command(command)
    if exit_code:
        message = 'Failed to update NTP and DNS servers'
        logger.error(message)
        logger.error('\nCMD: {}\nEC: {}\nSTDOUT:{}\nSTDERR:{}'.format(command, exit_code, stdout, stderr))
        raise RuntimeError(message)


def _run_update_deploy(ssh_client, logger):
    """Not sure what "update_deploy" does, but it has to run...

    :Returns: None

    :Raises: RuntimeError

    :param ssh_client: An established ssh connection to the ECS instance
    :type ssh_client: vlab_ecs_api.lib.worker.remote_shell.SSHClient

    :param logger: The task logging object
    :type logger: logging.LoggerAdapter
    """
    update_deploy = '/home/admin/bin/update_deploy'
    command = "{} {} {}".format(PRIME_SUDO, update_deploy, ECS_VM_LOGFILE)
    stdout, stderr, exit_code = ssh_client.exec_command(command)
    if exit_code:
        message = 'Failed to run update_deploy'
        logger.error(message)
        logger.error('\nCMD: {}\nSTDOUT:{}\nSTDERR:{}'.format(command, stdout, stderr))
        raise RuntimeError(message)


def _run_step1(ssh_client, logger):
    """Execute the "step-1" command to finish preparing the VM to be an ECS appliance

    :Returns: None

    :Raises: RuntimeError

    :param ssh_client: An established ssh connection to the ECS instance
    :type ssh_client: vlab_ecs_api.lib.worker.remote_shell.SSHClient

    :param logger: The task logging object
    :type logger: logging.LoggerAdapter
    """
    step1 = '/home/admin/bin/ova-step1'
    command = "{} {} {}".format(PRIME_SUDO, step1, ECS_VM_LOGFILE)
    stdout, stderr, exit_code = ssh_client.exec_command(command)
    if exit_code:
        stdout, stderr, exit_code = ssh_client.exec_command(command)
        # not sure why, but this typically fails the first time, but works the 2nd
        if exit_code:
            message = 'Failed to run step1'
            logger.error(message)
            logger.error('\nCMD: {}\nSTDOUT:{}\nSTDERR:{}'.format(command, stdout, stderr))
            raise RuntimeError(message)


def _run_step2(ssh_client, logger):
    """Execute the "step-2" command to finish the ECS bootstrapping process

    :Returns: None

    :Raises: RuntimeError

    :param ssh_client: An established ssh connection to the ECS instance
    :type ssh_client: vlab_ecs_api.lib.worker.remote_shell.SSHClient

    :param logger: The task logging object
    :type logger: logging.LoggerAdapter
    """
    step2 = '/home/admin/bin/ova-step2'
    command = "{} {} {}".format(PRIME_SUDO, step2, ECS_VM_LOGFILE)
    stdout, stderr, exit_code = ssh_client.exec_command(command)
    if exit_code:
        message = 'Failed to run step2'
        logger.error(message)
        logger.error('\nCMD: {}\nSTDOUT:{}\nSTDERR:{}'.format(command, stdout, stderr))
        raise RuntimeError(message)

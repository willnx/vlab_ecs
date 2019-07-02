# -*- coding: UTF-8 -*-
import paramiko


class SSHClient:
    """An API-similar implementation paramiko.client.SSHClient that blocks on
    remote command execution.

    :param hostname: The IP or FQDN of the remote server to access.
    :type hostname: String

    :param port: The TCP to connect to.
    :type port: Integer

    :param username: Who to login as on the remote server.
    :type username: String

    :param password: The user's password
    :type password: String

    :param missing_host_key_policy: What to do when the SSH key of the remote server is new/unkonwn
    :type missing_host_key_policy: paramiko.client.MissingHostKeyPolicy
    """
    def __init__(self, hostname, port, username, password, missing_host_key_policy=paramiko.client.AutoAddPolicy):
        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password
        self._ssh = paramiko.client.SSHClient()
        self._ssh.set_missing_host_key_policy(missing_host_key_policy)
        self._ssh.connect(hostname=self._hostname,
                          port=self._port,
                          username=self._username,
                          password=self._password)
        self._ssh.invoke_shell() # Load all the env stuff, just like a normal shell!

    @staticmethod
    def _block_on_command(channel):
        """Read stdin and stdout while a command executes to completion.

        Failure to read stdin and/or stdout can cause that socket buffer to fill.
        If one of those buffers fills, the command will appear to "hang" to the client.

        :Returns: Tuple (stdout, stderr, exit_code)

        :param channel: The SSH channel the command is executing within
        :type channel: paramiko.channel.Channel
        """
        # The old pattern in Py2 would be to create a list, append to it, then
        # after all the data has been collected, call join() to form the final
        # response. In Py3 with bytes, the += operator is more performant and
        # what "other language" users would expect.
        stdout = b''
        stderr = b''
        exit_code = -1
        while (channel.recv_stderr_ready() or channel.recv_ready() or channel.send_ready()):
            if channel.recv_ready():
                stdout += channel.recv(4096)
            if channel.recv_stderr_ready():
                stderr += channel.recv_stderr(4096)
            if channel.exit_status_ready():
                break
        exit_code = channel.recv_exit_status()
        return stdout.decode(), stderr.decode(), exit_code

    def exec_command(self, command, get_pty=True, **kwargs):
        """Just like Paramiko's SSHClient.exec_command, expect blocking and no
        file-like object response.

        :Returns: Tuple (stdout, stderr, exit_code)

        :param command: The CLI command to run. Syntax should be 1-for-1 to normal SSH/Shell
        :type command: String

        :param get_pty: Obtain a pseudoterminal. Default is True
        :type get_pty: Boolean
        """
        transport = self._ssh.get_transport()
        channel = transport.open_session()
        if get_pty:
            channel.get_pty()
        channel.exec_command(command, **kwargs)
        stdout, stderr, exit_code = self._block_on_command(channel)
        return stdout, stderr, exit_code

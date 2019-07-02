# -*- coding: UTF-8 -*-
"""
A suite of tests for the functions in tasks.py
"""
import unittest
from unittest.mock import patch, MagicMock

from vlab_ecs_api.lib.worker import tasks


class TestTasks(unittest.TestCase):
    """A set of test cases for tasks.py"""
    @patch.object(tasks, 'vmware')
    def test_show_ok(self, fake_vmware):
        """``show`` returns a dictionary when everything works as expected"""
        fake_vmware.show_ecs.return_value = {'worked': True}

        output = tasks.show(username='bob', txn_id='myId')
        expected = {'content' : {'worked': True}, 'error': None, 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_show_value_error(self, fake_vmware):
        """``show`` sets the error in the dictionary to the ValueError message"""
        fake_vmware.show_ecs.side_effect = [ValueError("testing")]

        output = tasks.show(username='bob', txn_id='myId')
        expected = {'content' : {}, 'error': 'testing', 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_create_ok(self, fake_vmware):
        """``create`` returns a dictionary when everything works as expected"""
        fake_vmware.create_ecs.return_value = {'worked': True}

        output = tasks.create(username='bob',
                              machine_name='ecsBox',
                              image='0.0.1',
                              network='someLAN',
                              txn_id='myId')
        expected = {'content' : {'worked': True}, 'error': None, 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_create_value_error(self, fake_vmware):
        """``create`` sets the error in the dictionary to the ValueError message"""
        fake_vmware.create_ecs.side_effect = [ValueError("testing")]

        output = tasks.create(username='bob',
                              machine_name='ecsBox',
                              image='0.0.1',
                              network='someLAN',
                              txn_id='myId')
        expected = {'content' : {}, 'error': 'testing', 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_delete_ok(self, fake_vmware):
        """``delete`` returns a dictionary when everything works as expected"""
        fake_vmware.delete_ecs.return_value = {'worked': True}

        output = tasks.delete(username='bob', machine_name='ecsBox', txn_id='myId')
        expected = {'content' : {}, 'error': None, 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_delete_value_error(self, fake_vmware):
        """``delete`` sets the error in the dictionary to the ValueError message"""
        fake_vmware.delete_ecs.side_effect = [ValueError("testing")]

        output = tasks.delete(username='bob', machine_name='ecsBox', txn_id='myId')
        expected = {'content' : {}, 'error': 'testing', 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_image(self, fake_vmware):
        """``image`` returns a dictionary when everything works as expected"""
        fake_vmware.list_images.return_value = ['3.2.2']

        output = tasks.image(txn_id='myId')
        expected = {'content' : {'image' : ['3.2.2']}, 'error': None, 'params' : {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_modify_network(self, fake_vmware):
        """``modify_network`` returns an empty content dictionary upon success"""
        output = tasks.modify_network(username='pat',
                                      machine_name='myEcs',
                                      new_network='wootTown',
                                      txn_id='someTransactionID')
        expected = {'content': {}, 'error': None, 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    def test_modify_network_error(self, fake_vmware):
        """``modify_network`` Catches ValueError, and sets the response accordingly"""
        fake_vmware.update_network.side_effect = ValueError('some bad input')

        output = tasks.modify_network(username='pat',
                                      machine_name='myEcs',
                                      new_network='wootTown',
                                      txn_id='someTransactionID')

        expected = {'content': {}, 'error': 'some bad input', 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    @patch.object(tasks, 'setup_ecs')
    def test_config_ok(self, fake_setup_ecs, fake_vmware):
        """``config`` returns a dictionary when everything works as expected"""
        fake_vmware.show_ecs.return_value = {'myECSbox' : {'meta': {'configured' : False}}}

        output = tasks.config(username='alice',
                              machine_name='myECSbox',
                              ssh_port=50022,
                              gateway_ip='10.8.6.1',
                              ecs_ip='192.168.1.65',
                              txn_id='aabbcc')
        expected = {'content': {}, 'error': None, 'params': {}}

        self.assertEqual(output, expected)

    @patch.object(tasks, 'vmware')
    @patch.object(tasks, 'setup_ecs')
    def test_config_meta(self, fake_setup_ecs, fake_vmware):
        """``config`` updates the VM meta data upon success"""
        fake_vmware.show_ecs.return_value = {'myECSbox' : {'meta': {'configured' : False}}}

        tasks.config(username='alice',
                     machine_name='myECSbox',
                     ssh_port=50022,
                     gateway_ip='10.8.6.1',
                     ecs_ip='192.168.1.65',
                     txn_id='aabbcc')

        self.assertTrue(fake_vmware.set_meta.called)

    @patch.object(tasks, 'vmware')
    @patch.object(tasks, 'setup_ecs')
    def test_config_already_config(self, fake_setup_ecs, fake_vmware):
        """``config`` does not attempt to configure an already configured ECS instance"""
        fake_vmware.show_ecs.return_value = {'myECSbox' : {'meta': {'configured' : True}}}

        tasks.config(username='alice',
                     machine_name='myECSbox',
                     ssh_port=50022,
                     gateway_ip='10.8.6.1',
                     ecs_ip='192.168.1.65',
                     txn_id='aabbcc')

        self.assertFalse(fake_setup_ecs.configure.called)

    @patch.object(tasks, 'vmware')
    @patch.object(tasks, 'setup_ecs')
    def test_config_already_config_error(self, fake_setup_ecs, fake_vmware):
        """``config``  Returns an error message if the ECS instance is already configured"""
        fake_vmware.show_ecs.return_value = {'myECSbox' : {'meta': {'configured' : True}}}

        output = tasks.config(username='alice',
                              machine_name='myECSbox',
                              ssh_port=50022,
                              gateway_ip='10.8.6.1',
                              ecs_ip='192.168.1.65',
                              txn_id='aabbcc')
        expected = {'content': {}, 'error': 'Unable to configure an already configured ECS instance', 'params': {}}

        self.assertFalse(fake_setup_ecs.configure.called)


    @patch.object(tasks, 'vmware')
    @patch.object(tasks, 'setup_ecs')
    def test_config_value_error(self, fake_setup_ecs, fake_vmware):
        """``config`` returns an error message upon catching a ValueError"""
        fake_vmware.show_ecs.side_effect = ValueError('testing')

        output = tasks.config(username='alice',
                              machine_name='myECSbox',
                              ssh_port=50022,
                              gateway_ip='10.8.6.1',
                              ecs_ip='192.168.1.65',
                              txn_id='aabbcc')

        expected = {'content': {}, 'error': 'testing', 'params': {}}

        self.assertFalse(fake_setup_ecs.configure.called)

    @patch.object(tasks, 'vmware')
    @patch.object(tasks, 'setup_ecs')
    def test_config_runtime_error(self, fake_setup_ecs, fake_vmware):
        """``config`` returns an error message upon catching a RuntimeError"""
        fake_vmware.show_ecs.side_effect = RuntimeError('testing')

        output = tasks.config(username='alice',
                              machine_name='myECSbox',
                              ssh_port=50022,
                              gateway_ip='10.8.6.1',
                              ecs_ip='192.168.1.65',
                              txn_id='aabbcc')

        expected = {'content': {}, 'error': 'testing', 'params': {}}

        self.assertFalse(fake_setup_ecs.configure.called)

    @patch.object(tasks, 'vmware')
    @patch.object(tasks, 'setup_ecs')
    def test_config_ok(self, fake_setup_ecs, fake_vmware):
        """``config`` returns a dictionary when everything works as expected"""
        fake_vmware.show_ecs.return_value = {'myECSbox' : {'meta': {'configured' : False}}}

        output = tasks.config(username='alice',
                              machine_name='someOtherBox',
                              ssh_port=50022,
                              gateway_ip='10.8.6.1',
                              ecs_ip='192.168.1.65',
                              txn_id='aabbcc')
        expected = {'content': {}, 'error': 'No such ECS instanced named someOtherBox found', 'params': {}}

        self.assertEqual(output, expected)


if __name__ == '__main__':
    unittest.main()

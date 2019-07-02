# -*- coding: UTF-8 -*-
"""
A suite of tests for the ecs object
"""
import unittest
from unittest.mock import patch, MagicMock

import ujson
from flask import Flask
from vlab_api_common import flask_common
from vlab_api_common.http_auth import generate_v2_test_token


from vlab_ecs_api.lib.views import ecs


class TestEcsView(unittest.TestCase):
    """A set of test cases for the EcsView object"""
    @classmethod
    def setUpClass(cls):
        """Runs once for the whole test suite"""
        cls.token = generate_v2_test_token(username='bob')

    @classmethod
    def setUp(cls):
        """Runs before every test case"""
        app = Flask(__name__)
        ecs.EcsView.register(app)
        app.config['TESTING'] = True
        cls.app = app.test_client()
        # Mock Celery
        app.celery_app = MagicMock()
        cls.fake_task = MagicMock()
        cls.fake_task.id = 'asdf-asdf-asdf'
        app.celery_app.send_task.return_value = cls.fake_task

    def test_v1_deprecated(self):
        """EcsView - GET on /api/1/inf/ecs returns an HTTP 404"""
        resp = self.app.get('/api/1/inf/ecs',
                            headers={'X-Auth': self.token})

        status = resp.status_code
        expected = 404

        self.assertEqual(status, expected)

    def test_get_task(self):
        """EcsView - GET on /api/2/inf/ecs returns a task-id"""
        resp = self.app.get('/api/2/inf/ecs',
                            headers={'X-Auth': self.token})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_get_task_link(self):
        """EcsView - GET on /api/2/inf/ecs sets the Link header"""
        resp = self.app.get('/api/2/inf/ecs',
                            headers={'X-Auth': self.token})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/ecs/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)

    def test_post_task(self):
        """EcsView - POST on /api/2/inf/ecs returns a task-id"""
        resp = self.app.post('/api/2/inf/ecs',
                             headers={'X-Auth': self.token},
                             json={'network': "someLAN",
                                   'name': "myEcsBox",
                                   'image': "someVersion"})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_post_task_link(self):
        """EcsView - POST on /api/2/inf/ecs sets the Link header"""
        resp = self.app.post('/api/2/inf/ecs',
                             headers={'X-Auth': self.token},
                             json={'network': "someLAN",
                                   'name': "myEcsBox",
                                   'image': "someVersion"})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/ecs/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)

    def test_delete_task(self):
        """EcsView - DELETE on /api/2/inf/ecs returns a task-id"""
        resp = self.app.delete('/api/2/inf/ecs',
                               headers={'X-Auth': self.token},
                               json={'name' : 'myEcsBox'})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_delete_task_link(self):
        """EcsView - DELETE on /api/2/inf/ecs sets the Link header"""
        resp = self.app.delete('/api/2/inf/ecs',
                               headers={'X-Auth': self.token},
                               json={'name' : 'myEcsBox'})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/ecs/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)

    def test_image(self):
        """EcsView - GET on the ./image end point returns the a task-id"""
        resp = self.app.get('/api/2/inf/ecs/image',
                            headers={'X-Auth': self.token})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_image(self):
        """EcsView - GET on the ./image end point sets the Link header"""
        resp = self.app.get('/api/2/inf/ecs/image',
                            headers={'X-Auth': self.token})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/ecs/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)

    def test_post_config_task(self):
        """EcsView - POST on /api/2/inf/ecs/config returns a task-id"""
        resp = self.app.post('/api/2/inf/ecs/config',
                             headers={'X-Auth': self.token},
                             json={'name': "myEcsBox",
                                   'ssh_port': 9001,
                                   'gateway_ip': '10.1.1.1',
                                   'ecs_ip': '192.168.1.32'})

        task_id = resp.json['content']['task-id']
        expected = 'asdf-asdf-asdf'

        self.assertEqual(task_id, expected)

    def test_post_task_config_link(self):
        """EcsView - POST on /api/2/inf/ecs/config sets the Link header"""
        resp = self.app.post('/api/2/inf/ecs/config',
                             headers={'X-Auth': self.token},
                             json={'name': "myEcsBox",
                                   'ssh_port': 9001,
                                   'gateway_ip': '10.1.1.1',
                                   'ecs_ip': '192.168.1.32'})

        task_id = resp.headers['Link']
        expected = '<https://localhost/api/2/inf/ecs/task/asdf-asdf-asdf>; rel=status'

        self.assertEqual(task_id, expected)


if __name__ == '__main__':
    unittest.main()

# -*- coding: UTF-8 -*-
"""
A suite of tests for the healthcheck API end point
"""
import unittest

from flask import Flask

from vlab_ecs_api.lib.views import healthcheck


class TestHealthView(unittest.TestCase):
    """A set of test cases for the HealthView object"""

    @classmethod
    def setUp(cls):
        """Runs before every test case"""
        app = Flask(__name__)
        healthcheck.HealthView.register(app)
        app.config['TESTING'] = True
        cls.app = app.test_client()

    def test_health_check(self):
        """A simple test to verify the /api/1/inf/ecs/healthcheck end point works"""
        resp = self.app.get('/api/1/inf/ecs/healthcheck')

        expected = 200

        self.assertEqual(expected, resp.status_code)


if __name__ == '__main__':
    unittest.main()

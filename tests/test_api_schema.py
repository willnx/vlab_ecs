# -*- coding: UTF-8 -*-
"""
A suite of tests for the HTTP API schemas
"""
import unittest

from jsonschema import Draft4Validator, validate, ValidationError
from vlab_ecs_api.lib.views import ecs


class TestEcsViewSchema(unittest.TestCase):
    """A set of test cases for the schemas of /api/1/inf/ecs"""

    def test_post_schema(self):
        """The schema defined for POST on is valid"""
        try:
            Draft4Validator.check_schema(ecs.EcsView.POST_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)


    def test_get_schema(self):
        """The schema defined for GET on is valid"""
        try:
            Draft4Validator.check_schema(ecs.EcsView.GET_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)

    def test_delete_schema(self):
        """The schema defined for DELETE on is valid"""
        try:
            Draft4Validator.check_schema(ecs.EcsView.DELETE_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)

    def test_iamges_schema(self):
        """The schema defined for GET on /images is valid"""
        try:
            Draft4Validator.check_schema(ecs.EcsView.IMAGES_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)


if __name__ == '__main__':
    unittest.main()

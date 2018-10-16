# -*- coding: UTF-8 -*-
"""
All the things can override via Environment variables are keep in this one file.

.. note::
    Any and all values that *are* passwords must contain the string 'AUTH' in
    the name of the constant. This is how we avoid logging passwords.
"""
from os import environ
from collections import namedtuple, OrderedDict


DEFINED = OrderedDict([
            ('VLAB_ECS_LOG_LEVEL', environ.get('VLAB_ECS_LOG_LEVEL', 'INFO')),
            ('INF_VCENTER_SERVER', environ.get('INF_VCENTER_SERVER', 'localhost')),
            ('INF_VCENTER_PORT', int(environ.get('INFO_VCENTER_PORT', 443))),
            ('INF_VCENTER_USER', environ.get('INF_VCENTER_USER', 'tester')),
            ('INF_VCENTER_PASSWORD', environ.get('INF_VCENTER_PASSWORD', 'a')),
            ('INF_VCENTER_DATASTORE', environ.get('INF_VCENTER_DATASTORE', 'VM-Storage')),
            ('INF_VCENTER_RESORUCE_POOL', environ.get('INF_VCENTER_RESORUCE_POOL', 'Resources')),
            ('INF_VCENTER_TOP_LVL_DIR', environ.get('INF_VCENTER_TOP_LVL_DIR', 'vlab')),
            ('INF_VCENTER_VERIFY_CERT', environ.get('INF_VCENTER_VERIFY_CERT', False)),
            ('VLAB_MESSAGE_BROKER', environ.get('VLAB_MESSAGE_BROKER', 'ecs-broker')),
            ('VLAB_URL', environ.get('VLAB_URL', 'https://localhost')),
            ('VLAB_ECS_IMAGES_DIR', environ.get('VLAB_ECS_IMAGES_DIR', '/images')),
          ])

Constants = namedtuple('Constants', list(DEFINED.keys()))

# The '*' expands the list, just liked passing a function *args
const = Constants(*list(DEFINED.values()))

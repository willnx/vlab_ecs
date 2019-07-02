#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
ecs RESTful API
"""
from setuptools import setup, find_packages


setup(name="vlab-ecs-api",
      author="Nicholas Willhite,",
      author_email='willnx84@gmail.com',
      version='2019.07.02',
      packages=find_packages(),
      include_package_data=True,
      package_files={'vlab_ecs_api' : ['app.ini']},
      description="ecs",
      install_requires=['flask', 'ldap3', 'pyjwt', 'uwsgi', 'vlab-api-common',
                        'ujson', 'cryptography', 'vlab-inf-common', 'celery', 'paramiko']
      )

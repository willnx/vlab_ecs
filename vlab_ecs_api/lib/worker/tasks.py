# -*- coding: UTF-8 -*-
"""
Entry point logic for available backend worker tasks
"""
from celery import Celery
from vlab_api_common import get_task_logger

from vlab_ecs_api.lib import const
from vlab_ecs_api.lib.worker import vmware

app = Celery('ecs', backend='rpc://', broker=const.VLAB_MESSAGE_BROKER)


@app.task(name='ecs.show', bind=True)
def show(self, username, txn_id):
    """Obtain basic information about Ecs

    :Returns: Dictionary

    :param username: The name of the user who wants info about their default gateway
    :type username: String

    :param txn_id: A unique string supplied by the client to track the call through logs
    :type txn_id: String
    """
    logger = get_task_logger(txn_id=txn_id, task_id=self.request.id, loglevel=const.VLAB_ECS_LOG_LEVEL.upper())
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        info = vmware.show_ecs(username)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    else:
        logger.info('Task complete')
        resp['content'] = info
    return resp


@app.task(name='ecs.create', bind=True)
def create(self, username, machine_name, image, network, txn_id):
    """Deploy a new instance of Ecs

    :Returns: Dictionary

    :param username: The name of the user who wants to create a new Ecs
    :type username: String

    :param machine_name: The name of the new instance of Ecs
    :type machine_name: String

    :param image: The image/version of Ecs to create
    :type image: String

    :param network: The name of the network to connect the new Ecs instance up to
    :type network: String

    :param txn_id: A unique string supplied by the client to track the call through logs
    :type txn_id: String
    """
    logger = get_task_logger(txn_id=txn_id, task_id=self.request.id, loglevel=const.VLAB_ECS_LOG_LEVEL.upper())
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        resp['content'] = vmware.create_ecs(username, machine_name, image, network, logger)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    logger.info('Task complete')
    return resp


@app.task(name='ecs.delete', bind=True)
def delete(self, username, machine_name, txn_id):
    """Destroy an instance of Ecs

    :Returns: Dictionary

    :param username: The name of the user who wants to delete an instance of Ecs
    :type username: String

    :param machine_name: The name of the instance of Ecs
    :type machine_name: String

    :param txn_id: A unique string supplied by the client to track the call through logs
    :type txn_id: String
    """
    logger = get_task_logger(txn_id=txn_id, task_id=self.request.id, loglevel=const.VLAB_ECS_LOG_LEVEL.upper())
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        vmware.delete_ecs(username, machine_name, logger)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    else:
        logger.info('Task complete')
    return resp


@app.task(name='ecs.image', bind=True)
def image(self, txn_id):
    """Obtain a list of available images/versions of Ecs that can be created

    :Returns: Dictionary

    :param txn_id: A unique string supplied by the client to track the call through logs
    :type txn_id: String
    """
    logger = get_task_logger(txn_id=txn_id, task_id=self.request.id, loglevel=const.VLAB_ECS_LOG_LEVEL.upper())
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    resp['content'] = {'image': vmware.list_images()}
    logger.info('Task complete')
    return resp

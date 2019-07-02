# -*- coding: UTF-8 -*-
"""
Defines the RESTful API for the ECS service
"""
import ujson
from flask import current_app
from flask_classy import request, route, Response
from vlab_inf_common.views import MachineView
from vlab_inf_common.vmware import vCenter, vim
from vlab_api_common import describe, get_logger, requires, validate_input


from vlab_ecs_api.lib import const


logger = get_logger(__name__, loglevel=const.VLAB_ECS_LOG_LEVEL)


class EcsView(MachineView):
    """API end point manage ECS instances"""
    route_base = '/api/2/inf/ecs'
    RESOURCE = 'ecs'
    POST_SCHEMA = { "$schema": "http://json-schema.org/draft-04/schema#",
                    "type": "object",
                    "description": "Create a ecs",
                    "properties": {
                        "name": {
                            "description": "The name to give your Ecs instance",
                            "type": "string"
                        },
                        "image": {
                            "description": "The image/version of Ecs to create",
                            "type": "string"
                        },
                        "network": {
                            "description": "The network to hook the Ecs instance up to",
                            "type": "string"
                        }
                    },
                    "required": ["name", "image", "network"]
                  }
    DELETE_SCHEMA = {"$schema": "http://json-schema.org/draft-04/schema#",
                     "description": "Destroy a Ecs",
                     "type": "object",
                     "properties": {
                        "name": {
                            "description": "The name of the Ecs instance to destroy",
                            "type": "string"
                        }
                     },
                     "required": ["name"]
                    }
    GET_SCHEMA = {"$schema": "http://json-schema.org/draft-04/schema#",
                  "description": "Display the Ecs instances you own"
                 }
    IMAGES_SCHEMA = {"$schema": "http://json-schema.org/draft-04/schema#",
                     "description": "View available versions of Ecs that can be created"
                    }
    CONFIG_SCHEMA = {"$schema": "http://json-schema.org/draft-04/schema#",
                     "description" : "Configure ECS",
                     "type": "object",
                     "properties": {
                        "name": {
                            "description": "The name of the ECS instance",
                            "type": "string"
                        },
                        "ssh_port": {
                            "description": "The SSH port to connect to, because ECS requires a TTY to configure",
                            "type": "number"
                        },
                        "gateway_ip": {
                            "description" : "The vLab NAT gateway of the user configuring an ECS instance",
                            "type": "string"
                        },
                        "ecs_ip": {
                            "description": "The IP (inside the NAT) of the ECS instance",
                            "type": "string"
                        }
                     },
                     "required": ["name", "ssh_port", "gateway_ip", "ecs_ip"]
                    }

    @requires(verify=const.VLAB_VERIFY_TOKEN, version=2)
    @describe(post=POST_SCHEMA, delete=DELETE_SCHEMA, get=GET_SCHEMA)
    def get(self, *args, **kwargs):
        """Display the ECS instances you own"""
        username = kwargs['token']['username']
        txn_id = request.headers.get('X-REQUEST-ID', 'noId')
        resp_data = {'user' : username}
        task = current_app.celery_app.send_task('ecs.show', [username, txn_id])
        resp_data['content'] = {'task-id': task.id}
        resp = Response(ujson.dumps(resp_data))
        resp.status_code = 202
        resp.headers.add('Link', '<{0}{1}/task/{2}>; rel=status'.format(const.VLAB_URL, self.route_base, task.id))
        return resp

    @requires(verify=const.VLAB_VERIFY_TOKEN, version=2)
    @validate_input(schema=POST_SCHEMA)
    def post(self, *args, **kwargs):
        """Create an ECS instance"""
        username = kwargs['token']['username']
        txn_id = request.headers.get('X-REQUEST-ID', 'noId')
        resp_data = {'user' : username}
        body = kwargs['body']
        machine_name = body['name']
        image = body['image']
        network = '{}_{}'.format(username, body['network'])
        task = current_app.celery_app.send_task('ecs.create', [username, machine_name, image, network, txn_id])
        resp_data['content'] = {'task-id': task.id}
        resp = Response(ujson.dumps(resp_data))
        resp.status_code = 202
        resp.headers.add('Link', '<{0}{1}/task/{2}>; rel=status'.format(const.VLAB_URL, self.route_base, task.id))
        return resp

    @requires(verify=const.VLAB_VERIFY_TOKEN, version=2)
    @validate_input(schema=DELETE_SCHEMA)
    def delete(self, *args, **kwargs):
        """Destroy an ECS instance"""
        username = kwargs['token']['username']
        txn_id = request.headers.get('X-REQUEST-ID', 'noId')
        resp_data = {'user' : username}
        machine_name = kwargs['body']['name']
        task = current_app.celery_app.send_task('ecs.delete', [username, machine_name, txn_id])
        resp_data['content'] = {'task-id': task.id}
        resp = Response(ujson.dumps(resp_data))
        resp.status_code = 202
        resp.headers.add('Link', '<{0}{1}/task/{2}>; rel=status'.format(const.VLAB_URL, self.route_base, task.id))
        return resp

    @route('/image', methods=["GET"])
    @requires(verify=const.VLAB_VERIFY_TOKEN, version=2)
    @describe(get=IMAGES_SCHEMA)
    def image(self, *args, **kwargs):
        """Show available versions of Ecs that can be deployed"""
        username = kwargs['token']['username']
        txn_id = request.headers.get('X-REQUEST-ID', 'noId')
        resp_data = {'user' : username}
        task = current_app.celery_app.send_task('ecs.image', [txn_id])
        resp_data['content'] = {'task-id': task.id}
        resp = Response(ujson.dumps(resp_data))
        resp.status_code = 202
        resp.headers.add('Link', '<{0}{1}/task/{2}>; rel=status'.format(const.VLAB_URL, self.route_base, task.id))
        return resp

    @route('/config', methods=["POST"])
    @requires(verify=const.VLAB_VERIFY_TOKEN, version=2)
    @describe(post=CONFIG_SCHEMA)
    @validate_input(schema=CONFIG_SCHEMA)
    def config(self, *args, **kwargs):
        """Configure the ECS instance into a usable thingy"""
        status_code = 202
        username = kwargs['token']['username']
        txn_id = request.headers.get('X-REQUEST-ID', 'noId')
        ssh_port = kwargs['body']['ssh_port']
        gateway_ip = kwargs['body']['gateway_ip']
        ecs_ip = kwargs['body']['ecs_ip']
        machine_name = kwargs['body']['name']
        resp_data = {'user' : username}
        task = current_app.celery_app.send_task('ecs.config', [username, machine_name, ssh_port, gateway_ip, ecs_ip, txn_id])
        resp_data['content'] = {'task-id': task.id}
        resp = Response(ujson.dumps(resp_data))
        resp.status_code = 202
        resp.headers.add('Link', '<{0}{1}/task/{2}>; rel=status'.format(const.VLAB_URL, self.route_base, task.id))
        return resp

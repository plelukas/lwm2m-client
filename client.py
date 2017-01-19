#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging

from enum import Enum

import aiocoap
from aiocoap.resource import Site, ObservableResource
from aiocoap.protocol import Context
from aiocoap.message import Message
from aiocoap.numbers.codes import Code

from model import ClientModel
from encoder import JSONEncoder


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class MediaType(Enum):
    LINK = 40
    TEXT = 1541
    TLV = 1542
    JSON = 1543
    OPAQUE = 1544


# NOTE: cannot implements cancel_observation: no render method for RESET coap message

class RequestsHandler(ObservableResource):

    # dict of: {path: token};   on observe add key to this dict, on cancel remove it
    observed_objects = dict()
    observe_interval = 5

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.encoder = JSONEncoder(self.model)

    # handle GET method (either observe or read) (request is a Message object)
    @asyncio.coroutine
    def render_get(self, request):
        message_details = self.get_message_details(request)
        if request.opt.observe is not None:
            if request.opt.observe == 0:
                logger.info("Requested observe at: {}".format(request.opt.uri_path))
                return self.handle_observe(message_details['path'], request.token)
            elif request.opt.observe == 1:
                logger.info("Requested cancel observation at: {}".format(message_details['path']))
                return self.handle_cancel_observe(message_details['path'], request.token)
            else:
                return Message(code=Code.METHOD_NOT_ALLOWED)
        else:
            logger.info("Requested read at: {}".format(request.opt.uri_path))
            return self.handle_read(message_details['path'])

    # handle PUT method (write)
    @asyncio.coroutine
    def render_put(self, request):
        message_details = self.get_message_details(request)
        logger.info("Requested write at: {} with payload: {}".format(message_details['path'], message_details['payload']))
        return self.handle_write(message_details)

    # handle POST method (execute)
    @asyncio.coroutine
    def render_post(self, request):
        message_details = self.get_message_details(request)
        logger.info("Requested execute at: {} with arguments: {}".format(message_details['path'], message_details['payload']))
        return self.handle_execute(message_details)

    # handle DELETE method (delete)
    @asyncio.coroutine
    def render_delete(self, request):
        return Message(code=Code.METHOD_NOT_ALLOWED)

    def get_message_details(self, request):
        return dict(path=request.opt.uri_path, payload=request.payload, format=request.opt.content_format)

    def handle_read(self, path):
        if len(path) == 2:
            result = Message(code=Code.CONTENT, payload=self.encoder.encode_read_instance(path))
            result.opt.content_format = MediaType.JSON.value
        elif len(path) == 3:
            result = Message(code=Code.CONTENT, payload=self.encoder.encode_read_resource(path))
            result.opt.content_format = MediaType.JSON.value
        else:
            result = Message(code=Code.BAD_REQUEST)
        return result

    def _notify(self, path, token):
        if len(path) == 2:
            result = Message(code=Code.CONTENT, payload=self.encoder.encode_read_instance(path), token=token)
        else:
            result = Message(code=Code.CONTENT, payload=self.encoder.encode_read_resource(path), token=token)
        result.opt.content_format = MediaType.JSON.value
        result.token = token
        self.updated_state(result)

    async def notify_observe(self, path):
        while True:
            await asyncio.sleep(self.observe_interval)

            token = self.observed_objects.get(path)
            if token is None:
                break
            self._notify(path, token)

    def handle_observe(self, path, token):
        if len(path) == 2:
            result = Message(code=Code.CONTENT, payload=self.encoder.encode_read_instance(path), token=token)
        elif len(path) == 3:
            result = Message(code=Code.CONTENT, payload=self.encoder.encode_read_resource(path), token=token)
        else:
            return Message(code=Code.BAD_REQUEST)

        # for now do observe as simple read
        # already_observed = self.observed_objects.get(path)
        # self.observed_objects[path] = token
        # if not already_observed:
        #     asyncio.ensure_future(self.notify_observe(path))

        result.opt.content_format = MediaType.JSON.value
        result.opt.observe = 0
        return result

    def handle_cancel_observe(self, path, token):
        self.observed_objects.pop(path, None)
        result = Message(code=Code.CONTENT, token=token)
        result.opt.content_format = MediaType.JSON.value
        return result

    def handle_write(self, message_details):
        # accept only json (for now)
        if message_details['format'] != MediaType.JSON.value:
            return Message(code=Code.BAD_REQUEST)

        if self.encoder.encode_write(message_details['path'], message_details['payload']):
            return Message(code=Code.CHANGED)
        return Message(code=Code.NOT_ACCEPTABLE)

    def handle_execute(self, message_details):
        if len(message_details['path']) != 3:
            return Message(code=Code.BAD_REQUEST)
        params_list = message_details['payload'].decode() or None
        if params_list:
            params_list = params_list.split(',')
        if self.model.handle_resource_exec(message_details['path'], params_list):
            return Message(code=Code.CHANGED)
        return Message(code=Code.NOT_FOUND)



class Client(Site):

    endpoint_name = "My_lwm2m_client"  # endpoint client name
    lifetime = 86400  # default
    binding = "UQ"  # binding mode
    model = None # model for objects and object instances
    requests_handler = None
    location = None
    timewait = 27

    def __init__(self, model=ClientModel(), server_name="192.168.1.94", server_port=5683):
        super().__init__()
        self.model = model
        self.server_name = server_name
        self.server_port = server_port

        self.requests_handler = RequestsHandler(self.model)

        # add observers
        for iter_path in model.get_instances_iter_paths():
            self.add_resource(iter_path, self.requests_handler)
        for iter_path in model.get_resources_iter_paths():
            self.add_resource(iter_path, self.requests_handler)

    @asyncio.coroutine
    def run(self):
        yield from asyncio.ensure_future(self.register())
        asyncio.sleep(self.timewait)
        asyncio.ensure_future(self.update())

    @asyncio.coroutine
    def register(self):
        self.context = yield from Context.create_server_context(self, bind=('::', 0))

        # send POST message registration
        register = Message(code=Code.POST, payload=self.model.get_objects_links().encode())
        register.opt.uri_host = self.server_name
        register.opt.uri_port = self.server_port
        # iterable over uris; ex: /rd/1  ->  ('rd', '1')
        register.opt.uri_path = ('rd',)
        # iterable over queries
        register.opt.uri_query = ('ep={}'.format(self.endpoint_name), 'lt={}'.format(self.lifetime),
                                  'b={}'.format(self.binding))

        # send the registration message
        response = yield from self.context.request(register).response

        if response.code != Code.CREATED:
            raise Exception("Unable to register. {}".format(response.code))

        self.location = response.opt.location_path[1].decode()
        logger.info("Registered at path: /{}/{}".format(response.opt.location_path[0].decode(), self.location))

    @asyncio.coroutine
    def update(self):
        # send POST update registration message
        update = Message(code=Code.POST)
        update.opt.uri_host = self.server_name
        update.opt.uri_port = self.server_port
        update.opt.uri_path = ('rd', self.location)

        response = yield from self.context.request(update).response

        if response.code != Code.CHANGED:
            # error while updating
            logger.warn("Registration update error. Code: {}".format(response.code))
            asyncio.ensure_future(self.register())
        else:
            logger.info("Registration update successfull. Next one in {} seconds".format(self.timewait))
            yield from asyncio.sleep(self.timewait)
            asyncio.ensure_future(self.update())

    @asyncio.coroutine
    def deregister(self):
        # send DELETE de-registration message
        deregister = Message(code=Code.DELETE)
        deregister.opt.uri_host = self.server_name
        deregister.opt.uri_port = self.server_port
        deregister.opt.uri_path = ('rd', self.location)

        response = self.context.request(deregister).response
        if response.code == Code.DELETED:
            logger.info("Deregistration from location: /rd/{} successfull.".format(self.location))
        else:
            logger.info("Couldn't deregister. Error code: {}".format(response.code))

if __name__ == '__main__':
    client = Client()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(client.run())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        asyncio.wait_for(client.deregister(), 2000)
        loop.close()
        exit(0)



#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging

from aiocoap.resource import Site
from aiocoap.protocol import Context
from aiocoap.message import Message
from aiocoap.numbers.codes import Code

from model import ClientModel


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class Client(Site):

    endpoint_name = "My_lwm2m_client"  # endpoint client name
    lifetime = 86400  # default
    binding = "UQ"  # binding mode
    model = None # model for objects and object instances
    location = None
    timewait = 27

    def __init__(self, model=ClientModel(), server_name="127.0.0.1", server_port=5683):
        super().__init__()
        self.model = model
        self.server_name = server_name
        self.server_port = server_port

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

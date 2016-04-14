import logging
import json

from .exc import BaseError, MessageError
from .environment import Environment
from . import messages

logger = logging.getLogger(__name__)


class AppBase:
    def __init__(self):
        """ Called before started ws server """
        pass

    async def __call__(self, server, client_id):
        """ Called when recived message """
        raise NotImplemented


class App(AppBase):

    handlers = {}

    env_class = Environment
    client_envs = {}
    messages = messages

    @property
    def clients(self):
        return self.client_envs.values()

    async def __call__(self, server, client_id):
        env = self.env_class(self, server, client_id)
        self.client_envs[client_id] = env
        try:
            while True:
                try:
                    raw_message =  await server.recv(client_id)
                    message = self.messages.Message.from_json(raw_message)
                    handler = self.handlers.get(message['name'])
                    if not handler:
                        raise MessageError(
                           'Handler "{}" not allowed'.format(message['handler']))
                    await handler(env, message['body'])
                except BaseError as e:
                    raise e
                    logger.debug(str(e))
                    error_message = self.messages.ErrorMessage(str(e), e.code)
                    await server.send(client_id, error_message.to_json())
        finally:
            del self.client_envs[client_id]


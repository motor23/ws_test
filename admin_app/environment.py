
class Environment:

    def __init__(self, app, server, client_id):
        self.app = app
        self._server = server
        self._client_id = client_id

    async def send_to(self, clients, name, body=None):
        for client in clients:
            message = self.app.messages.Message(name, body)
            await client._send(message.to_json())

    async def send(self, name, body=None):
        await self.send_to([self], name, body)

    async def send_to_all(self, name, body=None):
        await self.send_to(self.app.clients, name, body)

    def remote_address(self):
        return  server.get_remote_address(self._client_id)

    async def _send(self, value):
        await self._server.send(self._client_id, value)

    async def disconnect(self, code, reason):
        return self._server.disconnect(self._client_id, code, reason)

    async def ping(self):
        return self._server.ping(self._client_id)


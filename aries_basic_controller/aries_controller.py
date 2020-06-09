from aiohttp import (
    web,
    ClientSession,
    ClientRequest,
    ClientResponse,
    ClientError,
    ClientTimeout,
)
from pubsub import pub
import asyncio

from .connections_controller import ConnectionsController


class AriesAgentController:

    def __init__(self, webhook_host: str, webhook_port: int, webhook_base, connections: bool, admin_url: str):

        self.app = web.Application()
        self.webhook_site = None
        self.admin_url = admin_url
        self.webhook_host = webhook_host
        self.webhook_port = webhook_port
        self.connections_controller = None
        self.client_session: ClientSession = ClientSession()
        if connections:
            self.connections_controller = ConnectionsController(self.app, webhook_base, admin_url, self.client_session)
        self.proc = None

    async def register_connections_listener(self, listener):
        pub.subscribe(listener, "connections")

    async def register_messages_listener(self, listener):
        pub.subscribe(listener, "basicmessages")

    async def listen_webhooks(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        self.webhook_site = web.TCPSite(runner, self.webhook_host, self.webhook_port)
        await self.webhook_site.start()

    async def terminate(self):
        # loop = asyncio.get_event_loop()
        # if self.proc:
        #     await loop.run_in_executor(None, self._terminate)
        await self.client_session.close()
        if self.webhook_site:
            await self.webhook_site.stop()




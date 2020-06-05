
from aiohttp import (
    web,
    ClientSession,
    ClientRequest,
    ClientResponse,
    ClientError,
    ClientTimeout,
)

import asyncio

from connections_controller import ConnectionsController

class AriesAgentController:

    def __init__(self, webhook_port: str, webhook_base, connections: bool, admin_base: str):

        self.app = web.Application()
        self.webhook_site = None
        self.admin_base = admin_base
        self.webhook_port = webhook_port
        self.connections_controller = None
        if connections:
            self.connections_controller = ConnectionsController(self.app, webhook_base, admin_base)

    async def listen_webhooks(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        self.webhook_site = web.TCPSite(runner, "0.0.0.0", self.webhook_port)
        await self.webhook_site.start()

    async def terminate(self):
        loop = asyncio.get_event_loop()
        if self.proc:
            await loop.run_in_executor(None, self._terminate)
        await self.client_session.close()
        if self.webhook_site:
            await self.webhook_site.stop()

aries = AriesAgentController("443", "0.0.0.0", True, "https://demo1.myid.africa")
aries.listen_webhooks()
aries.terminate()
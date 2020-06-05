from base_controller import BaseController

from aiohttp import (
    web,
    ClientSession,
    ClientRequest,
    ClientResponse,
    ClientError,
    ClientTimeout,
)
import logging

logger = logging.getLogger(__name__)

class ConnectionsController(BaseController):

    def __init__(self, web_app, webhook_base: str, admin_base: str, client_session: ClientSession):
        super().__init__(web_app, webhook_base, admin_base, client_session)
        self.connections_hook = self.webhook_base + "/topic/connections/"
        #self.web_app.add_routes([web.post(self.connections_hook, self.connections_hook)])

    async def connection_hook(self, request: ClientRequest):
        payload = await request.json()
        print(payload)

        connection_id = payload['connection_id']
        state = payload['state']

        ### Throw some event ...
        return web.Response(status=200)

    ### TODO refactor to extract out generic base - /connections
    async def get_connections(self):
        connections = await self.admin_GET("/connections")
        return connections

    async def get_connection(self, connection_id: str):
        connection = await self.admin_GET(f"/connection/{connection_id}")
        return connection

    async def create_invitation(self, alias: str=None, role: str=None, auto_accept: bool=False):
        ### TODO add in variables
        invite_details = await self.admin_POST("/connections/create-invitation")
        return invite_details

    async def receive_invitation(self, connection_details: str):
        connection = await self.admin_POST("/connections/receive-invitation", connection_details)
        logger.debug("Connection Received - " + connection["connection_id"])
        return connection


    async def accept_invitation(self, connection_id: str):
        response = await self.admin_POST(f"/connections/{connection_id}/accept-invitation")
        return response

    async def accept_request(self, connection_id: str):
        response = await self.admin_POST(f"/connections/{connection_id}/accept-request")
        return response

    async def remove_connection(self, connection_id):
        response = await self.admin_POST(f"/connections/{connection_id}")
        return response

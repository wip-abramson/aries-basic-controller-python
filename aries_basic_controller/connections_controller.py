from .base_controller import BaseController

from pubsub import pub

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

    def __init__(self, admin_url: str, client_session: ClientSession):
        super().__init__(admin_url, client_session)

    ### TODO refactor to extract out generic base - /connections
    async def get_connections(self):
        connections = await self.admin_GET("/connections")
        return connections

    async def get_connection(self, connection_id: str):
        connection = await self.admin_GET(f"/connections/{connection_id}")
        return connection

    async def create_invitation(self, alias: str=None, role: str=None, auto_accept: bool=False):
        ### TODO add in arguments
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

    async def send_message(self, connection_id, msg):
        response = await self.admin_POST(f"/connections/{connection_id}/send-message", {"content": msg})
        return response

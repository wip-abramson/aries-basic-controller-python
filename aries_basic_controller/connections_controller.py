from .base_controller import BaseController
from .connection import Connection

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
        self.connections = []

    # @staticmethod
    # def default_handler():

    # TODO Add Logging here!
    def default_handler(self, payload):
        connection_id = payload["connection_id"]
        state = payload["state"]
        logger.debug(f"connections hook for {connection_id} with state: {state}")
        for connection in self.connections:
            if connection.id == connection_id:
                connection.update_state(state)
                logger.debug(f"{connection_id} state updated")

    ## Combines receive and accept connection api calls
    async def accept_connection(self, invitation):
        response = await self.receive_invitation(invitation)

        accepted = await self.accept_invitation(response["connection_id"])
        print("ACCEPTED CONNECTION - ", accepted)
        return accepted


    ### TODO refactor to extract out generic base - /connections
    async def get_connections(self):
        connections = await self.admin_GET("/connections")
        return connections

    async def get_connection(self, connection_id: str):
        connection = await self.admin_GET(f"/connections/{connection_id}")
        return connection

    async def create_invitation(self, alias: str = None, auto_accept: bool = None, public: bool = False, multi_use: bool = False ):
        invite_details = await self.admin_POST("/connections/create-invitation",params = {"alias": alias, "auto_accept": auto_accept, "public": public, "multi_use": multi_use })
        connection = Connection(invite_details["connection_id"], "invitation")
        self.connections.append(connection)
        return invite_details

    async def receive_invitation(self, connection_details: str, alias: str = None, auto_accept: bool = None):
        response = await self.admin_POST("/connections/receive-invitation", connection_details, params = {"alias": alias, "auto_accept": auto_accept})
        connection = Connection(response["connection_id"], response["state"])
        self.connections.append(connection)
        logger.debug("Connection Received - " + connection.id)
        return response

    async def accept_invitation(self, connection_id: str, my_label: str = None, my_endpoint: str = None):
        response = await self.admin_POST(f"/connections/{connection_id}/accept-invitation",params = {"my_label": my_label, "my_endpoint": my_endpoint})
        return response


    async def accept_request(self, connection_id: str, my_endpoint: str = None):
        # TODO get if connection_id is in request state, else throw error
        connection_ready = await self.check_connection_ready(connection_id, "request")
        print(connection_ready)
        if connection_ready:
            response = await self.admin_POST(f"/connections/{connection_id}/accept-request",params = {"my_endpoint": my_endpoint})
            return response
        else:
            ## TODO create proper error classes
            raise Exception("The connection is not in the request state")


    async def remove_connection(self, connection_id):
        response = await self.admin_POST(f"/connections/{connection_id}")
        return response



    async def check_connection_ready(self, connection_id, state):
        stored = False
        for connection in self.connections:
            if connection.id == connection_id:
                await connection.detect_state_ready(state)
                return True
        if not stored:
            try:
                response = self.get_connection(connection_id)
                connection = Connection(response["connection_id"], response["state"])
                await connection.detect_state_ready(state)
                return True
            except Exception:
                return False


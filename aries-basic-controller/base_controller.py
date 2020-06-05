from aiohttp import (
    web,
    ClientSession,
    ClientRequest,
    ClientResponse,
    ClientError,
    ClientTimeout,
)

import asyncio
import logging

import json

EVENT_LOGGER = logging.getLogger("event")


class repr_json:
    def __init__(self, val):
        self.val = val

    def __repr__(self) -> str:
        if isinstance(self.val, str):
            return self.val
        return json.dumps(self.val, indent=4)


class BaseController:

    def __init__(self, web_app: str, webhook_base: str, admin_base: str):
        self.web_app = web_app
        self.admin_url = admin_base
        self.webhook_base = webhook_base
        self.client_session: ClientSession = ClientSession()
        self.webhook_site = None


    async def admin_request(
        self, method, path, data=None, text=False, params=None
    ) -> ClientResponse:
        params = {k: v for (k, v) in (params or {}).items() if v is not None}
        async with self.client_session.request(
            method, self.admin_url + path, json=data, params=params
        ) as resp:
            resp.raise_for_status()
            resp_text = await resp.text()
            if not resp_text and not text:
                return None
            if not text:
                try:
                    return json.loads(resp_text)
                except json.JSONDecodeError as e:
                    raise Exception(f"Error decoding JSON: {resp_text}") from e
            return resp_text


    async def admin_GET(self, path, text=False, params=None) -> ClientResponse:
        try:
            EVENT_LOGGER.debug("Controller GET %s request to Agent", path)
            response = await self.admin_request("GET", path, None, text, params)
            EVENT_LOGGER.debug(
                "Response from GET %s received: \n%s", path, repr_json(response),
            )
            return response
        except ClientError as e:
            self.log(f"Error during GET {path}: {str(e)}")
            raise

    async def admin_POST(
            self, path, data=None, text=False, params=None
    ) -> ClientResponse:
        try:
            EVENT_LOGGER.debug(
                "Controller POST %s request to Agent%s",
                path,
                (" with data: \n{}".format(repr_json(data)) if data else ""),
            )
            response = await self.admin_request("POST", path, data, text, params)
            EVENT_LOGGER.debug(
                "Response from POST %s received: \n%s", path, repr_json(response),
            )
            return response
        except ClientError as e:
            self.log(f"Error during POST {path}: {str(e)}")
            raise



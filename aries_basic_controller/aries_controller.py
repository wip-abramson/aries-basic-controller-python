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
import os
import subprocess
import functools
from timeit import default_timer
import json

from .utils import flatten, log_json, log_msg, log_timer, output_reader
from .connections_controller import ConnectionsController

class AriesAgentController:

    def __init__(self, webhook_host: str, webhook_port: int, admin_url: str, connections: bool, webhook_base: str = ""):

        self.webhook_site = None
        self.admin_url = admin_url
        if webhook_base:
            self.webhook_base = webhook_base
        else:
            self.webhook_base = ""
        self.webhook_host = webhook_host
        self.webhook_port = webhook_port
        self.connections_controller = None
        self.client_session: ClientSession = ClientSession()
        if connections:
            self.connections_controller = ConnectionsController(self.admin_url, self.client_session)
        self.proc = None
        self.endpoint = admin_url
        self._connection_ready = asyncio.Future()


    def register_listeners(self, listeners):
        for listener in listeners:
            log_msg(listener["handler"])
            log_msg(listener["topic"])
            pub.subscribe(listener["handler"], listener["topic"])

    # async def listen_webhooks(self):
    #     app = web.Application()
    #     app.add_routes([web.post(self.webhook_base + "/topic/{topic}/", self._receive_webhook)])
    #     runner = web.AppRunner(app)
    #     await runner.setup()
    #     self.webhook_site = web.TCPSite(runner, self.webhook_host, self.webhook_port)
    #     await self.webhook_site.start()

    async def listen_webhooks(self, webhook_port):
        self.webhook_port = webhook_port
        #UNCOMMENT BELOW FOR ORIGINAL CODE
        # if RUN_MODE == "pwd":
        #     self.webhook_url = f"http://localhost:{str(webhook_port)}/webhooks"
        # else:
        #     self.webhook_url = (
        #         f"http://{self.external_host}:{str(webhook_port)}/webhooks"
        #     )
        # COMMENT BELOW LINE FOR ORIGINAL CODE
        self.webhook_url = f"http://localhost:{str(webhook_port)}/webhooks"

        app = web.Application()
        app.add_routes([web.post("/webhooks/topic/{topic}/", self._receive_webhook)])
        runner = web.AppRunner(app)
        await runner.setup()
        self.webhook_site = web.TCPSite(runner, "0.0.0.0", webhook_port)
        await self.webhook_site.start()

    async def _receive_webhook(self, request: ClientRequest):
        topic = request.match_info["topic"]
        payload = await request.json()
        await self.handle_webhook(topic, payload)
        return web.Response(status=200)

    async def handle_webhook(self, topic, payload):
        # log_msg(f"Hanlde {topic}")
        # log_msg(payload)
        pub.sendMessage(topic, payload=payload)
        return web.Response(status=200)


    async def terminate(self):
        # loop = asyncio.get_event_loop()
        # if self.proc:
        #     await loop.run_in_executor(None, self._terminate)
        await self.client_session.close()
        if self.webhook_site:
            await self.webhook_site.stop()

    async def start_process(
        self, python_path: str = None, bin_path: str = None, wait: bool = True
    ):
        my_env = os.environ.copy()
        # python_path = DEFAULT_PYTHON_PATH if python_path is None else python_path
        # if python_path:
        #     my_env["PYTHONPATH"] = python_path

        agent_args = self.get_process_args(bin_path)

        # start agent sub-process
        loop = asyncio.get_event_loop()
        self.proc = await loop.run_in_executor(
            None, self._process, agent_args, my_env, loop
        )
        if wait:
            await asyncio.sleep(1.0)
            await self.detect_process()

    def get_process_args(self, bin_path: str = None):
        # cmd_path = "aca-py"
        # if bin_path is None:
        #     bin_path = DEFAULT_BIN_PATH
        # if bin_path:
        #     cmd_path = os.path.join(bin_path, cmd_path)
        # return list(flatten((["python3", cmd_path, "start"], self.get_agent_args())))
        return "test"

    def _process(self, args, env, loop):
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            encoding="utf-8",
        )
        loop.run_in_executor(
            None,
            output_reader,
            proc.stdout,
            functools.partial(self.handle_output, source="stdout"),
        )
        loop.run_in_executor(
            None,
            output_reader,
            proc.stderr,
            functools.partial(self.handle_output, source="stderr"),
        )
        return proc

    def handle_output(self, *output, source: str = None, **kwargs):
        end = "" if source else "\n"
        if source == "stderr":
            color = "fg:ansired"
        elif not source:
            color = self.color or "fg:ansiblue"
        else:
            color = None
        log_msg(*output, color=color, prefix=self.prefix_str, end=end, **kwargs)

    async def detect_process(self):
        async def fetch_status(url: str, timeout: float):
            text = None
            start = default_timer()
            async with ClientSession(timeout=ClientTimeout(total=3.0)) as session:
                while default_timer() - start < timeout:
                    try:
                        async with session.get(url) as resp:
                            if resp.status == 200:
                                text = await resp.text()
                                break
                    except (ClientError, asyncio.TimeoutError):
                        pass
                    await asyncio.sleep(0.5)
            return text

        status_url = self.admin_url + "/status"
        # status_text = await fetch_status(status_url, START_TIMEOUT)
        status_text = await fetch_status(status_url, 30.0)

        if not status_text:
            raise Exception(
                "Timed out waiting for agent process to start. "
                + f"Admin URL: {status_url}"
            )
        ok = False
        try:
            status = json.loads(status_text)
            ok = isinstance(status, dict) and "version" in status
        except json.JSONDecodeError:
            pass
        if not ok:
            raise Exception(
                f"Unexpected response from agent process. Admin URL: {status_url}"
            )

    @property
    def connection_ready(self):
        return self._connection_ready.done() and self._connection_ready.result()

    async def detect_connection(self):
        await self._connection_ready




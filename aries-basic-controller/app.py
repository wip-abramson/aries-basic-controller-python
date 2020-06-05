

import os
import asyncio

from .aries_controller import AriesAgentController


async def start_agent():
    aries = AriesAgentController("443", "0.0.0.0", True, "https://demo1.myid.africa")
    connections = await aries.connections_controller.get_connections()
    print(connections)
    for connection in connections:
        print(connection)

    invite = await aries.connections_controller.create_invitation(alias="Will")
    print("Invite", invite)
    await aries.terminate()


if __name__ == "__main__":
    # aries.listen_webhooks()
    try:
        asyncio.get_event_loop().run_until_complete(start_agent())
    except KeyboardInterrupt:
        os._exit(1)

    asyncio.sleep(100)

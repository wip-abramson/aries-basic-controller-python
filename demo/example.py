import os
import asyncio

from aries_basic_controller.aries_controller import AriesAgentController

from dotenv import load_dotenv
load_dotenv()

admin_url = os.getenv('ADMIN_URL')
webhook_host = os.getenv('WEBHOOK_HOST')
webhook_port = os.getenv('WEBHOOK_PORT')
webhook_base = os.getenv('WEBHOOK_BASE')

async def start_agent():
    aries = AriesAgentController(webhook_host, webhook_port, webhook_base, True, admin_url)
    AriesAgentController()
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


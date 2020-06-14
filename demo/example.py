import os
import asyncio
import time

from aries_basic_controller.aries_controller import AriesAgentController

from dotenv import load_dotenv
load_dotenv()

RESEARCHER_ADMIN_URL = os.getenv('RESEARCHER_ADMIN_URL')
RESEARCHER_WEBHOOK_PORT = os.getenv('RESEARCHER_WEBHOOK_PORT')
RESEARCHER_WEBHOOK_HOST = os.getenv('RESEARCHER_WEBHOOK_HOST')
RESEARCHER_WEBHOOK_BASE = os.getenv('RESEARCHER_WEBHOOK_BASE')

DATA_ADMIN_URL = os.getenv('DATA_ADMIN_URL')
DATA_WEBHOOK_PORT = os.getenv('DATA_WEBHOOK_PORT')
DATA_WEBHOOK_HOST = os.getenv('DATA_WEBHOOK_HOST')
DATA_WEBHOOK_BASE = os.getenv('DATA_WEBHOOK_BASE')


async def start_agent():

    time.sleep(6)

    data_agent_controller = AriesAgentController(webhook_host=DATA_WEBHOOK_HOST, webhook_port=DATA_WEBHOOK_PORT,
                                               webhook_base=DATA_WEBHOOK_BASE, admin_url=DATA_ADMIN_URL, connections=True)



    researcher_agent_controller = AriesAgentController(webhook_host=RESEARCHER_WEBHOOK_HOST, webhook_port=RESEARCHER_WEBHOOK_PORT,
                                               webhook_base=RESEARCHER_WEBHOOK_BASE, admin_url=RESEARCHER_ADMIN_URL, connections=True)

    def connections_hook(payload):
        print(payload)
        print("THE CONNECTIONS HOOK WORKS")


    await researcher_agent_controller.listen_webhooks()

    await data_agent_controller.listen_webhooks()

    data_connection_listener = {
        "handler": connections_hook,
        "topic": "connections"
    }

    researcher_agent_controller.register_listeners([data_connection_listener])


    invite = await data_agent_controller.connections_controller.create_invitation(alias="Will")
    print("Invite", invite)

    response = await researcher_agent_controller.connections_controller.receive_invitation(invite["invitation"])
    print(response)

    accepted = await researcher_agent_controller.connections_controller.accept_invitation(response["connection_id"])

    print("Invite Accepted")
    print(accepted)

    connections = await data_agent_controller.connections_controller.get_connections()
    print("DATA AGENT CONNECTIONS")
    for connection in connections:
        print(connection)

    # success = await data_agent_controller.connections_controller.accept_request(invite["connection_id"])

    # print(success)
    time.sleep(20)
    await data_agent_controller.terminate()
    await researcher_agent_controller.terminate()


if __name__ == "__main__":
    # aries.listen_webhooks()

    try:
        asyncio.get_event_loop().run_until_complete(start_agent())
    except KeyboardInterrupt:
        os._exit(1)


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

    data_connection_id = None
    data_id_ready = asyncio.Future()

    def data_connections_hook(payload):
        connection_id = payload["connection_id"]
        print("Handle data connections ", connection_id)
        print(payload)
        if connection_id == data_connection_id:
            print("ID Equal")
            if payload["state"] == "request":
                print("Connection Request")
                asyncio.get_event_loop().run_until_complete(data_agent_controller.connections_controller.accept_request(connection_id))

            if payload["state"] == "active" and not data_id_ready.done():
                print("Connection Active", connection_id)
                data_id_ready.set_result(True)

    async def detect_connection():
        await data_id_ready

    @property
    def connection_ready():
        return data_id_ready.done() and data_id_ready.result()





    await researcher_agent_controller.listen_webhooks()

    await data_agent_controller.listen_webhooks()



    data_connection_listener = {
        "handler": data_connections_hook,
        "topic": "connections"
    }

    data_agent_controller.register_listeners([data_connection_listener])


    invite = await data_agent_controller.connections_controller.create_invitation(alias="Will")
    print("Invite", invite)

    data_connection_id = invite["connection_id"]

    response = await researcher_agent_controller.connections_controller.receive_invitation(invite["invitation"])
    print(response)

    accepted = await researcher_agent_controller.connections_controller.accept_invitation(response["connection_id"])

    print("Invite Accepted")
    print(accepted)

    connections = await data_agent_controller.connections_controller.get_connections()
    print("DATA AGENT CONNECTIONS")
    for connection in connections:
        print(connection)




    # print(success)
    time.sleep(200)
    await data_agent_controller.terminate()
    await researcher_agent_controller.terminate()


if __name__ == "__main__":
    # aries.listen_webhooks()

    try:
        asyncio.get_event_loop().run_until_complete(start_agent())
    except KeyboardInterrupt:
        os._exit(1)


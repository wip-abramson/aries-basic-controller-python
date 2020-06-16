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


    def research_messages_hook(payload):
        connection_id = payload["connection_id"]
        print("Handle research messages ", payload, connection_id)

    def data_messages_hook(payload):
        connection_id = payload["connection_id"]
        print("Handle data messages ", payload, connection_id)


    data_message_listener = {
        "handler": data_messages_hook,
        "topic": "basicmessages"
    }

    research_message_listener = {
        "handler": research_messages_hook,
        "topic": "basicmessages"
    }


    await researcher_agent_controller.listen_webhooks()

    await data_agent_controller.listen_webhooks()


    data_agent_controller.register_listeners([data_message_listener], defaults=True)
    researcher_agent_controller.register_listeners([research_message_listener], defaults=True)

    invite = await data_agent_controller.connections.create_invitation(alias="Will")
    print("Invite", invite)

    data_connection_id = invite["connection_id"]

    response = await researcher_agent_controller.connections.accept_connection(invite["invitation"])
    print(response)


    print("Researcher ID", response["connection_id"])
    researcher_id = response["connection_id"]
    print("Invite Accepted")
    print(response)


    connection = await data_agent_controller.connections.accept_request(data_connection_id)
    print("ACCEPT REQUEST")
    print(connection)

    connection = await data_agent_controller.connections.get_connection(data_connection_id)
    print("DATA AGENT CONNECTION")
    print(connection)

    while connection["state"] != "active":
        trust_ping = await data_agent_controller.connections.trust_ping(data_connection_id, "hello")
        print("TUST PING TO ACTIVATE CONNECTION - DATA -> RESEARCH")
        print(trust_ping)
        time.sleep(5)
        connection = await data_agent_controller.connections.get_connection(data_connection_id)

    trust_ping = await researcher_agent_controller.connections.trust_ping(researcher_id,"hello")
    print("TUST PING TO ACTIVATE CONNECTION - RESEARCH -> DATA")
    print(trust_ping)

    print("RESEARCHER ID {} DATA ID {}".format(researcher_id,data_connection_id))

    connection = await data_agent_controller.connections.get_connection(data_connection_id)
    print("DATA AGENT CONNECTION")
    print(connection)

    connection = await researcher_agent_controller.connections.get_connection(researcher_id)
    print("RESEARCH AGENT CONNECTION")
    print(connection)

    #send some basic messages
    message = await researcher_agent_controller.connections.send_message(researcher_id,"hello from researcher world!")
    print("BASIC MESSAGE - RESEARCH -> DATA")
    print(message)

    #send some basic messages
    message = await data_agent_controller.connections.send_message(data_connection_id,"hello from data world!")
    print("BASIC MESSAGE - DATA -> RESEARCH")
    print(message)

    for i in range(1, 10):
        message = await researcher_agent_controller.connections.send_message(researcher_id,
                                                                                        "ping")
        print("BASIC MESSAGE - RESEARCH -> DATA")
        message = await data_agent_controller.connections.send_message(data_connection_id,
                                                                                  "pong")
        print("BASIC MESSAGE - DATA -> RESEARCH")

    print("SUCCESS")
    time.sleep(2)
    await data_agent_controller.terminate()
    await researcher_agent_controller.terminate()


if __name__ == "__main__":

    try:
        asyncio.get_event_loop().run_until_complete(start_agent())
    except KeyboardInterrupt:
        os._exit(1)


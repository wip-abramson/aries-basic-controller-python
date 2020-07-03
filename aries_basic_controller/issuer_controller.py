from .base_controller import BaseController
from aiohttp import ClientSession, ClientResponseError
import logging

logger = logging.getLogger("aries_controller.issuer")

CRED_PREVIEW = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview"

class IssuerController(BaseController):

    def __init__(self, admin_url: str, client_session: ClientSession, connection_controller, wallet_controller,
                 schema_controller, definition_controller):
        super().__init__(admin_url, client_session)
        self.base_url = "/issue-credential"
        self.connections = connection_controller
        self.wallet = wallet_controller
        self.schema = schema_controller
        self.definitions = definition_controller

    # Fetch all credential exchange records
    async def get_records(self):

        return await self.admin_GET(f"{self.base_url}/records")

    async def get_record_by_id(self, cred_ex_id):
        return await self.admin_GET(f"{self.base_url}/{cred_ex_id}")

    # Send holder a credential, automating the entire flow
    # Need a credential body like this
    # {
    #     "issuer_did": "WgWxqztrNooG92RXvxSTWv",
    #     "schema_name": "preferences",
    #     "auto_remove": true,
    #     "credential_proposal": {
    #         "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
    #         "attributes": [
    #             {
    #                 "name": "favourite_drink",
    #                 "mime-type": "image/jpeg",
    #                 "value": "martini"
    #             }
    #         ]
    #     },
    #     "connection_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    #     "trace": true,
    #     "comment": "string",
    #     "cred_def_id": "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag",
    #     "schema_id": "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0",
    #     "schema_issuer_did": "WgWxqztrNooG92RXvxSTWv",
    #     "schema_version": "1.0"
    # }
    async def send_credential(self, connection_id, schema_id, cred_def_id, attributes, comment: str = "",
                              auto_remove: bool = True, trace: bool = True):
        ## TODO revist error handling
        # try:
            # response = await self.wallet.get_public_did()
            # issuer_did = response['result']['did']
            # if issuer_did is None:
            #     raise Exception("Agent must have a public DID")

        response = await self.connections.get_connection(connection_id)
        if response["state"] != "active":
            print("Connection not active")
            raise Exception("Connection must be active to send a credential")

        response = await self.schema.get_by_id(schema_id)
        schema = response["schema"]
        schema_name = schema["name"]
        # TODO extract into utils
        schema_issuer_id = schema_id.split(":")[0]
        #
        print("Schema issuer", schema_issuer_id)
        schema_version = schema["version"]
        issuer_did = cred_def_id.split(":")[0]
        print("Cred issuer", issuer_did)

        credential_body = {
            "issuer_did": issuer_did,
            "schema_name": schema_name,
            "auto_remove": auto_remove,
            "credential_proposal": {
                "@type": CRED_PREVIEW,
                "attributes": attributes
            },
            "connection_id": connection_id,
            "trace": trace,
            "comment": comment,
            "cred_def_id": cred_def_id,
            "schema_id": schema_id,
            "schema_issuer_did": schema_issuer_id,
            "schema_version": schema_version
        }
        return await self.admin_POST(f"{self.base_url}/send", data=credential_body)
        # except ClientResponseError:
        #     logger.error("Error calling api")
        #     return "ERROR"
        # except Exception:
        #     logger.error("The agent does not have a public DID")
        #     return "ERROR: The agent does not have a public DID"



    # Send Issuer a credential proposal
    # TODO proposal body needs spliting up. See above.
    async def send_proposal(self, proposal_body):
        return await self.admin_POST(f"{self.base_url}/send-proposal", data=proposal_body)

    # Send holder a credential offer, independent of any proposal with preview
    # TODO offer body needs spliting up. See above.
    async def send_offer(self, offer_body):
        return await self.admin_POST(f"{self.base_url}/send-offer", data=offer_body)

    # Send holder a credential offer in reference to a proposal with preview
    async def send_offer_for_record(self, cred_ex_id):
        return await self.admin_POST(f"{self.base_url}/records/{cred_ex_id}/send-offer")

    # Send issuer a credential request
    async def send_request_for_record(self, cred_ex_id):
        return await self.admin_POST(f"{self.base_url}/records/{cred_ex_id}/send-request")

    # Send holder a credential
    async def issue_credential(self, cred_ex_id):
        return await self.admin_POST(f"{self.base_url}/records/{cred_ex_id}/issue")

    # Store a received credential
    async def store_credential(self, cred_ex_id):
        return await self.admin_POST(f"{self.base_url}/records/{cred_ex_id}/send")

    # Revoke and issued credential
    async def revoke_credential(self, rev_reg_id, cred_rev_id, publish: bool = False):
        params = {
            "rev_reg_id": rev_reg_id,
            "cred_reg_id": cred_rev_id,
            "publish": publish
        }
        return await self.admin_POST(f"{self.base_url}/revoke", params=params)

    # Publish pending revocations
    async def publish_revocations(self):
        return await self.admin_POST(f"{self.base_url}/publish-revocations")

    # Remove an existing credential exchange record
    async def remove_record(self, cred_ex_id):
        return await self.admin_POST(f"{self.base_url}/records/{cred_ex_id}/remove")

    # Send a problem report for a credential exchange
    async def problem_report(self, cred_ex_id, explanation: str):
        body = {
            "explain_ltxt": explanation
        }

        return await self.admin_POST(f"{self.base_url}/records/{cred_ex_id}/problem-report", data=body)
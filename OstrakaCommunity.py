import os
import sys
from asyncio import ensure_future, get_event_loop
from PyInquirer import prompt, print_json

sys.path.append('../')

from pyipv8.ipv8.community import Community
from pyipv8.ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from pyipv8.ipv8.lazy_community import lazy_wrapper
# from pyipv8.ipv8.messaging.lazy_payload import VariablePayload, vp_compile
from pyipv8.ipv8_service import IPv8
from Transaction import Transaction


class OstrakaCommunity (Community):
    community_id = os.urandom(20)

    def __init__ (self, my_peer, endpoint, network):
        super().__init__(my_peer, endpoint, network)
        # Register the message handler for messages with the identifier "1".
        self.add_message_handler(0, self.on_message)
        # The Lamport clock this peer maintains.
        # This is for the example of global clock synchronization.
        self.collective_string = ""

    # get up to date with the blockchain
    def started (self):
        return

    @lazy_wrapper(Transaction)
    def on_message(self, peer, payload):
        self.collective_string = self.collective_string + payload.text
        print(self.collective_string)

    def broadcast_message (self, tx):
        for peer in self.get_peers:
            self.ez_send(peer, tx)

ipv8s = list()

async def start_communities():
    for i in [1, 2, 3]:
        builder = ConfigBuilder().clear_keys().clear_overlays()
        builder.add_key("my peer", "medium", f"ec{i}.pem")
        builder.add_overlay("OstrakaCommunity", "my peer", [WalkerDefinition(Strategy.RandomWalk, 10, {'timeout': 3.0})],
                            default_bootstrap_defs, {}, [('started',)])
        ipv8 = IPv8(builder.finalize(), extra_communities={'OstrakaCommunity': OstrakaCommunity})
        ipv8s.append(ipv8)
        await ipv8.start()

        #ipv8.get_overlays(OstrakaCommunity)???

answers = "go"
questions = [
    {
        'type': 'input',
        'name': 'message',
        'message': 'What to broadcast? (STOP to stop):',
    }
]

async def get_message ():
    while answers['message'] != 'STOP':
        answers = prompt(questions)
        # ipv8s[0].

ensure_future(start_communities())
get_event_loop().run_forever()
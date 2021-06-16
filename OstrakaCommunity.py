import os
import sys
from asyncio import ensure_future, get_event_loop
import asyncio
from PyInquirer import prompt, print_json

sys.path.append('../')

from pyipv8.ipv8.community import Community
from pyipv8.ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from pyipv8.ipv8.lazy_community import lazy_wrapper
from pyipv8.ipv8.messaging.lazy_payload import VariablePayload, vp_compile
from pyipv8.ipv8_service import IPv8
from Transaction import Transaction

@vp_compile
class MyMessage(VariablePayload):
    msg_id = 1  # The byte identifying this message, must be unique per community.
    format_list = ['varlenI']  # When reading data, we unpack an unsigned integer from it.
    names = ["msg"]  # We will name this unsigned integer "clock"

class OstrakaCommunity (Community):
    community_id = os.urandom(20)

    def __init__ (self, my_peer, endpoint, network):
        super().__init__(my_peer, endpoint, network)
        # Register the message handler for messages with the identifier "1".
        self.add_message_handler(1, self.on_message)
        # The Lamport clock this peer maintains.
        # This is for the example of global clock synchronization.
        self.collective_string = ""

    # get up to date with the blockchain
    def started (self):
        async def start_communication():
            print ('started')
            self.cancel_pending_task('start_communication')

        self.register_task("start_communication", start_communication, interval=5.0, delay=0)
        

    @lazy_wrapper(MyMessage)
    def on_message(self, peer, payload):
        print ("got a msg")
        self.collective_string = self.collective_string + payload.msg.decode()
        print(self.collective_string)

    def broadcast_message (self, msg):
        print("broadcasting:", msg, "to", self.get_peers())
        for peer in self.get_peers():
            self.ez_send(peer, msg)

ipv8s = list()
q = asyncio.Queue()

async def start_communities():
    for i in [1, 2, 3]:
        builder = ConfigBuilder().clear_keys().clear_overlays()
        builder.add_key("my peer", "medium", f"ec{i}.pem")
        builder.add_overlay("OstrakaCommunity", "my peer", [WalkerDefinition(Strategy.RandomWalk, 10, {'timeout': 3.0})],
                            default_bootstrap_defs, {}, [('started',)])
        ipv8 = IPv8(builder.finalize(), extra_communities={'OstrakaCommunity': OstrakaCommunity})
        ipv8s.append(ipv8)
        await ipv8.start()

        ostraka = ipv8s[0].get_overlay(OstrakaCommunity)

    while True:
        output = await q.get()
        ostraka.broadcast_message(MyMessage(output.encode()))


ensure_future(start_communities())
loop = get_event_loop()

def got_stdin_data(q):
    asyncio.ensure_future(q.put(sys.stdin.readline()))

loop.add_reader(sys.stdin, got_stdin_data, q)
loop.run_forever()



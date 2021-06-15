
import typing
import struct

import time

from enum import Enum, auto

from pyipv8.ipv8.messaging.serialization import Serializable

class Operation (Enum):
    TEST = auto()
    GRANT = auto()
    RESPOND = auto()
    MODIFY = auto()
    SEND = auto()

def packTest (text):
    return text

def unpackTest (text):
    return text

# packOpText = {
#     {Operation.TEST.value, packTest}
# }

class Transaction (Serializable):
    msg_id = 0
    format_list = ['B', 'varlenI', 'varlenI', 'varlenI', 'varlenI']

    def __init__ (self, op : Operation, sender, time : str, text, signature):
        self.op = op
        self.sender = sender
        self.time = struct.unpack("d", time)[0]
        self.text = text
        self.signature = signature

    def to_pack_list (self) -> typing.List[tuple]:
        return [
            ('B', self.op),
            ('varlenI', self.sender),
            ('varlenI', struct.pack("d", self.time)),
            ('varlenI', bytes(self.text, 'utf-8')),
            ('varlenI', self.signature),
        ]

    def __str__ (self):
        s = 'op:' + str(self.op) + ' '
        s = s + 'sender:' + str(self.sender) + ' '
        s = s + 'time:' + str(self.time) + ' '
        s = s + 'text:' + str(self.text) + ' '
        return 'signature:' + str(self.signature) 

    @classmethod
    def from_unpack_list(cls, *args) -> Serializable:  # pylint: disable=E0213
        return cls(*args)
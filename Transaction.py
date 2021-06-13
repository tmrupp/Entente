
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

class Transaction (Serializable):
    format_list = ['B', 'varlenI', 'varlenI', 'varlenI', 'varlenI']

    def __init__ (self, op : Operation, sender, time : str, text, signature):
        self.op = op
        self.sender = sender
        self.time = struct.unpack("d", time)[0]
        self.text = text # long string
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
        s = s + 'signature:' + str(self.signature) 

        return s


    @classmethod
    def from_unpack_list(cls, *args) -> Serializable:  # pylint: disable=E0213
        return cls(*args)
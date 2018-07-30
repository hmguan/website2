from . import proto_head
from pynsp.serialize import *
from . import proto_typedef as typedef

class proto_common_stream(proto_interface):
    """docstring for proto_common_stream"""
    def __init__(self):
        super(proto_common_stream, self).__init__()
        self.head_ = proto_head.proto_head()
        self.pkt_id = proto_int32(0)
        self.common_stream = proto_string()

    def length(self):
        return self.head_.length() + self.pkt_id.length() + self.common_stream.length()

    def serialize(self)->bytes:
        return self.head_.serialize() + self.pkt_id.serialize() + self.common_stream.serialize()

    def build(self,data,offset) -> int:
        offset = self.head_.build(data,offset)
        offset = self.pkt_id.build(data,offset)
        return self.common_stream.build(data,offset)
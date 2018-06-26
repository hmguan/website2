from agvmt.mtproto import mthead
from pynsp.serialize import *

PKTTYPE_COMMON_READ_BYID        = 0x00000104
PKTTYPE_COMMON_READ_BYID_ACK    = 0x80000104

class proto_common_read_item:
    def __init__(self):
        self.var_id = proto_int32()
        self.var_type = proto_int32()
        self.var_offset = proto_int32()
        self.var_length = proto_int32()

    def __del__(self):
        pass

    def length(self):
        return self.var_id.length() + self.var_type.length() + self.var_offset.length() + self.var_length.length()

    def serialize(self)->bytes:
        return self.var_id.serialize() + self.var_type.serialize() + self.var_offset.serialize() + self.var_length.serialize()

    def build(self, data, offset)->int:
        off = self.var_id.build(data, offset)
        off = self.var_type.build(data, off)
        off = self.var_offset.build(data, off)
        off = self.var_length.build(data, off)
        return off

class proto_common_read(proto_interface):
    def __init__(self):
        super(proto_common_read, self).__init__()
        self.phead = mthead.proto_head(_type = PKTTYPE_COMMON_READ_BYID)
        self.items = proto_vector(TYPE = proto_common_read_item )

    def __def__(self):
        pass

    def length(self):
        return self.phead.length() + self.items.length()

    def serialize(self)->bytes:
        return self.phead.serialize() + self.items.serialize()

    def build(self, data, offset)->int:
        off = self.phead.build(data, offset)
        off = self.items.build(data, off)
        return off

class proto_common():
        def __init__(self):
            self.var_id = proto_int32()
            self.var_type = proto_int32()
            self.var_offset = proto_int32()
            self.var_data = proto_binary()

        def __del__(self):
            pass

        def length(self):
            return self.var_id.length() + self.var_type.length() + self.var_offset.length() + self.var_data.length()

        def serialize(self) -> bytes:
            return self.var_id.serialize() + self.var_type.serialize() + self.var_offset.serialize() + self.var_data.serialize()

        def build(self, data, offset) -> int:
            off = self.var_id.build(data, offset)
            off = self.var_type.build(data, off)
            off = self.var_offset.build(data, off)
            off = self.var_data.build(data, off)
            return off

class proto_common_vct(proto_interface):
    def __init__(self):
        super(proto_common_vct, self).__init__()
        self.phead = mthead.proto_head(_type = PKTTYPE_COMMON_READ_BYID_ACK)
        self.items = proto_vector(TYPE = proto_common )

    def __def__(self):
        pass

    def length(self):
        return self.phead.length() + self.items.length()

    def serialize(self)->bytes:
        return self.phead.serialize() + self.items.serialize()

    def build(self, data, offset)->int:
        off = self.phead.build(data, offset)
        off = self.items.build(data, off)
        return off
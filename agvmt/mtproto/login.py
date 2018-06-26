from agvmt.mtproto import mthead
from pynsp.serialize import *

PKTTYPE_PRE_LOGIN               = 0x00000107
PKTTYPE_PRE_LOGIN_ACK           = 0x80000107

PKTTYPE_LOGIN_ROBOT             = 0x00000101
PKTTYPE_LOGIN_ROBOT_ACK         = 0x80000101

class proto_pre_login(proto_interface):
    def __init__(self):
        super(proto_pre_login, self).__init__()
        self.phead = mthead.proto_head()
        self.key = proto_binary()

    def __del__(self):
        pass

    def length(self)->int:
        return self.phead.length() + self.key.length()

    def serialize(self)->bytes:
        return self.phead.serialize() + self.key.serialize()

    def build(self, data, offset)->int:
        off = self.phead.build(data, offset)
        return self.key.build(data, off)

class proto_login(proto_interface):
    def __init__(self):
        super(proto_login, self).__init__
        self.phead = mthead.proto_head(_type = PKTTYPE_LOGIN_ROBOT)
        self.cct = proto_uint32(0x100 << 6)
        self.access = proto_uint32(0)
        self.ori = proto_binary()
        self.enc = proto_binary()

    def __del__(self):
        pass

    def length(self)->int:
        return self.phead.length() + self.cct.length() + self.access.length() + self.ori.length() + self.enc.length()

    def serialize(self)->bytes:
        return self.phead.serialize() + self.cct.serialize() + self.access.serialize() + self.ori.serialize() + self.enc.serialize()

    def build(self, data, offset)->int:
        off = self.phead.build(data, offset)
        off = self.cct.build(data, off)
        off = self.access.build(data, off)
        off = self.ori.build(data, off)
        off = self.enc.build(data, off)
        return off

proto_login_ack = mthead.proto_head
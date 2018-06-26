from . import proto_head as phead
from pynsp.serialize import *
from . import proto_typedef

class proto_pre_login(proto_interface):
    def __init__(self):
        super(proto_pre_login,self).__init__()
        self.phead=phead.proto_head()
        self.publickey=proto_binary()

    def __del__(self):

        pass

    def length(self)->int:
        return self.phead.length() + self.publickey.length()

    def serialize(self)->bytes:
        return self.phead.serialize() + self.publickey.serialize()

    def build(self, data, offset)->int:
        off = self.phead.build(data, offset)
        return self.publickey.build(data, off)

class proto_login(proto_interface):
    def __init__(self):
        super(proto_login, self).__init__()
        self.phead=phead.proto_head(_type=proto_typedef.PKTTYPE_AGV_SHELL_LOGIN)
        self.cct=proto_uint32(0)
        self.access=proto_uint32(0)
        self.ori = proto_binary()
        self.enc = proto_binary()

    def length(self)->int:
        return self.phead.length()+self.cct.length()+self.access.length()+self.ori.length()+self.enc.length()

    def serialize(self)->bytes:
        return self.phead.serialize()+self.cct.serialize()+self.access.serialize()+self.ori.serialize()+self.enc.serialize()

    def build(self, data, offset)->int:
        off=self.phead.build(data,offset)
        off=self.cct.build(data,off)
        off=self.access.build(data,off)
        off=self.ori.build(data,off)
        off=self.enc.build(data,off)
        return off
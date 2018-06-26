from pynsp import serialize
from agvmt.mtproto import mthead

kAgvInfoProto_heart_beat = 0
kAgvInfoProto_get_agvinfo = 1
kAgvInfoProto_set_agvinfo = 2
kAgvInfoProto_get_agvdetail = 3
kAgvInfoProto_set_agvdetail = 4
kAgvInfoProto_update_notify = 5
kAgvInfoProto_heart_beat_ack = 6

# error code
KAgvInfo_Errno_Ok = 0
KAgvInfo_Errno_Failed = 1

#method
kAgvinfo_Method_LAM_Local = 0
kAgvinfo_Method_LAM_Server = 1
kAgvinfo_Method_LAM_Real = 2

# status
AS_IGNORE = 0x7FFF   # load agvinfo only from xml file
AS_ONLINE = 1         # this vehicle is storage in xml file and it's online
AS_OFFLINE = 2         # this vehicle is storage in xml file but it's offline
AS_UNKNOWN = 3          # we can receive UDP report from client. but no @hwaddr can be match in xml file

class proto_agvattribute:
    def __init__(self):
        self.name = serialize.proto_string()
        self.describe = serialize.proto_string()

    def __del__(self):
        pass

    def length(self)->int:
        total = self.name.length()
        total += self.describe.length()
        return total

    def serialize(self)->bytes:
        return self.name.serialize() + self.describe.serialize()

    def build(self,data, offset)->int:
        off = self.name.build(data, offset)
        off = self.describe.build(data, off)
        return off

class proto_agvinfo:
    def __init__(self):
        super(proto_agvinfo, self).__init__()
        self.vhid = serialize.proto_uint32(0)
        self.vhtype = serialize.proto_uint32(0)
        self.inet = serialize.proto_string()
        self.mtport = serialize.proto_uint16(0)
        self.shport = serialize.proto_uint16(0)
        self.ftsport = serialize.proto_uint16(0)
        self.hwaddr = serialize.proto_string()
        self.status = serialize.proto_uint16(0)
        self.attrs = serialize.proto_vector(proto_agvattribute)

    def __del__(self):
        pass

    def length(self)->int:
        total = self.vhid.length()
        total += self.vhtype.length()
        total += self.inet.length()
        total += self.mtport.length()
        total += self.shport.length()
        total += self.ftsport.length()
        total += self.hwaddr.length()
        total += self.status.length()
        total += self.attrs.length()
        return total

    def serialize(self)->bytes:
        data = self.vhid.serialize()
        data += self.vhtype.serialize()
        data += self.inet.serialize()
        data += self.mtport.serialize()
        data += self.shport.serialize()
        data += self.ftsport.serialize()
        data += self.hwaddr.serialize()
        data += self.status.serialize()
        data += self.attrs.serialize()
        return data

    def build(self, data, offset)->int:
        off = self.vhid.build(data, offset)
        off = self.vhtype.build(data, off)
        off = self.inet.build(data, off)
        off = self.mtport.build(data, off)
        off = self.shport.build(data, off)
        off = self.ftsport.build(data, off)
        off = self.hwaddr.build(data, off)
        off = self.status.build(data, off)
        off = self.attrs.build(data, off)
        return off

class proto_req_agvinfo(serialize.proto_interface):
    def __init__(self):
        super(proto_req_agvinfo,self).__init__()
        self.head = mthead.proto_head()
        self.method = serialize.proto_uint8(0)
        self.info = serialize.proto_vector(proto_agvinfo)

    def __del__(self):
        pass

    def length(self)->int:
        total = self.head.length()
        total += self.method.length()
        total += self.info.length()
        return total

    def serialize(self)->bytes:
        data = self.head.serialize()
        data += self.method.serialize()
        data += self.info.serialize()
        return data

    def build(self, data, offset)->int:
        off = self.head.build(data, offset)
        off = self.method.build(data, off)
        off = self.info.build(data, off)
        return off
    
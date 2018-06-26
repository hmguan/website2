from agvmt.mtproto import mthead
from pynsp.serialize import *
import struct

PKTTYPE_KEEPALIVE_UDP       = 0x0000010D
PKTTYPE_KEEPALIVE_UDP_ACK   = 0x8000010D

class proto_discover_mt(proto_interface):
    def __init__(self):
        super(proto_discover_mt, self).__init__()
        self.phead = mthead.proto_head(_type = PKTTYPE_KEEPALIVE_UDP)
        self.address = str('\x00' * 16)
        self.port = proto_uint16(0)

    def __del__(self):
        pass

    def length(self)->int:
        total = 0
        total += self.phead.length()
        total += 16
        total += self.port.length()
        return total

    def serialize(self)->bytes:
        stream = self.phead.serialize()
        stream += struct.pack('16s', self.address.encode('utf-8'))
        stream += self.port.serialize()
        return stream

    def build(self, data, offset)->int:
        off = self.phead.build(data, offset)
        self.address = struct.unpack('16s', data[off:off + 16])[0].decode('utf-8')
        off += 16
        off = self.port.build(data, off)
        return off
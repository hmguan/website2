from pynsp.serialize import *

class proto_head(proto_interface):
    def __init__(self, _id = 0, _type = 0, _size = 0, _err = 0, _fd = 0, _token = 0):
        super(proto_head, self).__init__()
        self.id = proto_uint32(_id)
        self.type = proto_uint32(_type)
        self.size = proto_uint32(_size)
        self.err = proto_int32(_err)
        self.fd = proto_uint32(_fd)
        self.token = proto_uint32(_token)

    def __del__(self):
        pass

    def length(self)->int:
        return self.id.length() + \
            self.type.length() + \
            self.size.length() + \
            self.err.length() + \
            self.fd.length() + \
            self.token.length()

    def serialize(self)->bytes:
        return self.id.serialize() + \
            self.type.serialize() + \
            self.size.serialize() + \
            self.err.serialize() + \
            self.fd.serialize() + \
            self.token.serialize()

    def build(self, data, offset)->int:
        off = self.id.build(data, offset)
        off = self.type.build(data, off)
        off = self.size.build(data, off)
        off = self.err.build(data, off)
        off = self.fd.build(data, off)
        off = self.token.build(data, off)
        return off

    def set_pkt_size(self,size):
        self.size=proto_uint32(size)
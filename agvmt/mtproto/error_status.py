from pynsp.serialize import *


class proto_error(proto_interface):
    def __init__(self):
        super(proto_error,self).__init__()
        self.error = proto_uint32()

    def length(self)->int:
        return self.error.length()

    def serialize(self)->bytes:
        return self.error.serialize()

    def build(self, data, offset)->int:
        offset= self.error.build(data, offset)

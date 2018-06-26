from . import proto_head as phead
from pynsp.serialize import *

class proto_a_upgrade(proto_interface):
    def __init__(self):
        super(proto_a_upgrade,self).__init__()
        self.phead=phead.proto_head()
        self.file_size=proto_uint32(0)
        self.file_name=proto_string('')
        

    def __del__(self):

        pass

    def length(self)->int:
        return self.phead.length() + self.file_size.length() + self.file_name.length()

    def serialize(self)->bytes:
        return self.phead.serialize() + self.file_size.serialize() + self.file_name.serialize()

    def build(self, data, offset)->int:
        off = self.phead.build(data, offset)
        off = self.file_size.build(data, off)
        return self.file_name.build(data, off)


from pynsp.serialize import *

SIZEOF_HEAD = 24

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

PKTTYPE_KEEPALIVE_TCP       = 0x00000106
PKTTYPE_KEEPALIVE_TCP_ACK   = 0x80000106

class proto_keepalive(proto_head):
    def __init__(self):
        super(proto_keepalive, self).__init__(_type = PKTTYPE_KEEPALIVE_TCP, _size = SIZEOF_HEAD)

PKTTYPE_DBG_CLEAR_FAULT     = 0x00000403
PKTTYPE_DBG_CLEAR_FAULT_ACK = 0x80000403

class proto_clearfault(proto_head):
    def __init__(self):
        super(proto_clearfault, self).__init__(_type=PKTTYPE_DBG_CLEAR_FAULT, _size=SIZEOF_HEAD)

PKTTYPE_DBG_VARLS           =  0x00000402  #要求下位机报告所有的变量， 及其类型
PKTTYPE_DBG_VARLS_ACK       =  0x80000402

class proto_dug_varls(proto_head):
    def __init__(self):
        super(proto_dug_varls, self).__init__(_type=PKTTYPE_DBG_VARLS, _size=SIZEOF_HEAD)

class var_report_items:
    def __init__(self):
        self.var_id = proto_int()
        self.var_type = proto_int32()

    def __del__(self):
        pass

    def length(self):
        return self.var_id.length() + self.var_type.length()

    def serialize(self)->bytes:
        return self.var_id.serialize() + self.var_type.serialize()

    def build(self, data, offset)->int:
        off = self.var_id.build(data, offset)
        off = self.var_type.build(data, off)
        return off

class proto_var_report_items(proto_interface):
    def __init__(self):
        super(proto_var_report_items, self).__init__()
        self.phead = proto_head(_type = PKTTYPE_DBG_VARLS_ACK)
        self.items = proto_vector(TYPE = var_report_items )

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

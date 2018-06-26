import struct
from abc import ABCMeta,abstractmethod

############################################################# abstract base virtual class type ###############################################
class proto_interface(metaclass=ABCMeta):
    @abstractmethod
    def length(self)->int: 
        pass

    @abstractmethod
    def serialize(self)->bytes: 
        pass

    @abstractmethod
    def build(self, data, offset)->int: 
        pass

    def __init__(self): 
        pass

    def __call__(self): 
        pass

############################################################# CRT class type #############################################################
    # python3 no longer support class type 'long'
    # so, every integer is class type 'int'
class proto_int(proto_interface):
    def __init__(self, value = 0):
        super(proto_int, self).__init__()
        self.value = int(value)

    def length(self)->int:
        return 4

    def serialize(self)->bytes: 
        return struct.pack('i', self.value )

    def build(self, data, offset)->int:
        self.value = struct.unpack('i', data[offset:offset+self.length()])[0]
        return offset + self.length()

    # obj(value) will call __call__ operator, like operator() in c++
    # p = proto_int()
    # p(100) will call __call__ method and then self.value = 100
    def __call__(self, value):
        self.value = value

    # print('%d' % obj) will call __int__ operator
    def __int__(self):
        return self.value

    # print(obj) call __str__
    def __str__(self):
        return '{}'.format(self.value)

    # bin(X), hex(X), oct(X), O[X], O[X:] print('%x' % obj)... will call __index__ operator
    def __index__(self):
        return self.value

    def __eq__(self, value):
        return self.value == value

    def __add__(self, other):
        self.value += other
        return self

    def __iadd__(self, other):
        self.value += other
        return self

    __repr__ = __str__

class proto_int64(proto_int):
    def __init__(self, value = 0):
        super(proto_int64, self).__init__(value)

    def length(self)->int:
        return 8

    def serialize(self)->bytes: 
        return struct.pack('q', self.value )

    def build(self, data, offset)->int:
        self.value = struct.unpack('q', data[offset:offset+self.length()])[0]
        return offset + self.length()

class proto_uint64(proto_int64):
    def __init__(self, value = 0):
        super(proto_uint64, self).__init__(value)

    def serialize(self)->bytes: 
        return struct.pack('Q', self.value )

    def build(self, data, offset)->int:
        self.value = struct.unpack('Q', data[offset:offset+self.length()])[0]
        return offset + self.length()

class proto_int32(proto_int):
    def __init__(self, value = 0):
        super(proto_int32, self).__init__(value)

class proto_uint32(proto_int):
    def __init__(self, value = 0):
        super(proto_uint32, self).__init__(value)

    def serialize(self)->bytes: 
        return struct.pack('I', self.value )

    def build(self, data, offset)->int:
        self.value = struct.unpack('I', data[offset:offset+self.length()])[0]
        return offset + self.length()

class proto_int16(proto_int):
    def __init__(self, value = 0):
        super(proto_int16, self).__init__(value)

    def length(self)->int:
        return 2

    def serialize(self)->bytes: 
        return struct.pack('h', self.value )

    def build(self, data, offset)->int:
        self.value = struct.unpack('h', data[offset:offset+self.length()])[0]
        return offset + self.length()

class proto_uint16(proto_int16):
    def __init__(self, value = 0):
        super(proto_uint16, self).__init__(value)

    def serialize(self)->bytes: 
        return struct.pack('H', self.value )

    def build(self, data, offset)->int:
        self.value = struct.unpack('H', data[offset:offset+self.length()])[0]
        return offset + self.length()

class proto_int8(proto_int):
    def __init__(self, value = 0):
        super(proto_int8, self).__init__(value)

    def length(self)->int:
        return 1

    def serialize(self)->bytes: 
        return struct.pack('b', self.value )

    def build(self, data, offset)->int:
        self.value = struct.unpack('b', data[offset:offset+self.length()])[0]
        return offset + self.length()

class proto_uint8(proto_int8):
    def __init__(self, value = 0):
        super(proto_uint8, self).__init__(value)

    def serialize(self)->bytes: 
        return struct.pack('B', self.value )

    def build(self, data, offset)->int:
        self.value = struct.unpack('B', data[offset:offset+self.length()])[0]
        return offset + self.length()

class proto_double(proto_interface):
    def __init__(self,value=0):
        super(proto_double, self).__init__()
        self.value = float(value)

    def length(self) -> int:
        return 8

    def serialize(self) -> bytes:
        return struct.pack('d', self.value)

    def build(self, data, offset) -> int:
        self.value = struct.unpack('d', data[offset:offset + self.length()])[0]
        return offset + self.length()

    def __call__(self, value):
        self.value = value

    def __int__(self):
        return self.value


    def __str__(self):
        return '{}'.format(self.value)

    def __index__(self):
        return self.value

    def __eq__(self, value):
        return self.value == value

    def __add__(self, other):
        self.value += other
        return self

    def __iadd__(self, other):
        self.value += other
        return self

class proto_float(proto_interface):
    def __init__(self,value=0):
        super(proto_float, self).__init__()
        self.value = float(value)

    def length(self) -> int:
        return 4

    def serialize(self) -> bytes:
        return struct.pack('f', self.value)

    def build(self, data, offset) -> int:
        self.value = struct.unpack('f', data[offset:offset + self.length()])[0]
        return offset + self.length()

    def __call__(self, value):
        self.value = value

    def __int__(self):
        return self.value


    def __str__(self):
        return '{}'.format(self.value)

    def __index__(self):
        return self.value

    def __eq__(self, value):
        return self.value == value

    def __add__(self, other):
        self.value += other
        return self

    def __iadd__(self, other):
        self.value += other
        return self
############################################################# composite class type #############################################################
class proto_string(proto_interface):
    def __init__(self, string_=''):
        proto_interface.__init__(self)
        self.count = proto_int32(len(string_))
        self.value = str(string_)

    def length(self)->int:
        return self.count.length() + len(self.value)

    def serialize(self)->bytes: 
        self.count(len(self.value))
        return self.count.serialize() + struct.pack('{}s'.format(self.count.value), self.value.encode('utf-8'))

    def build(self, data, offset)->int:
        off = self.count.build(data, offset)
        if self.count.value > 0:
            self.value = struct.unpack('{}s'.format(self.count.value), data[off:off + self.count.value])[0].decode('utf-8')
            off += self.count.value
        return off

    def __add__(self, other):
        return self.value + other

    def __iadd__(self, other):
        self.value += other
        return self

    def __str__(self):
        return self.value

    __repr__ = __str__

    def __call__(self, string_):
        self.value = string_
        self.count(len(string_))

    def __iter__(self):
        return iter(self.value)

    def __next__(self):
        return next(self.value)

    def __len__(self):
        return len(self.value)

class proto_binary(proto_interface):
    def __init__(self, binary_=b''):
        proto_interface.__init__(self)
        self.count = proto_int32(len(binary_))
        self.value = bytes(binary_)

    def length(self)->int:
        return self.count.length() + len(self.value)

    def serialize(self)->bytes: 
        self.count(len(self.value))
        return self.count.serialize() + self.value

    def build(self, data, offset)->int:
        off = self.count.build(data, offset)
        if self.count.value > 0:
            self.value = data[off:off + self.count.value]
            off += self.count.value
        return off

    def __add__(self, other):
        return self.value + other

    def __iadd__(self, other):
        self.value += other
        return self

    def __str__(self):
        return str(self.value, encode='utf-8')

    __repr__ = __str__

    def __call__(self, binary_):
        self.value = binary_
        self.count(len(self.value))

    def __iter__(self):
        return iter(self.value)

    def __next__(self):
        return next(self.value)

    def __len__(self):
        return len(self.value)

class proto_vector(proto_interface, list):
    def __init__(self, TYPE):
        super(proto_vector, self).__init__()
        self.count = proto_int32(0)
        self.itype = TYPE

    def length(self)->int:
        total = self.count.length()
        for i in self:
            total += i.length()
        return total

    def serialize(self)->bytes: 
        self.count(len(self))
        stream = self.count.serialize()
        for i in self:
            stream += i.serialize()
        return stream

    def build(self, data, offset)->int:
        off = self.count.build(data, offset)
        for i in range(self.count.value):
            item = self.itype()
            off = item.build(data, off)
            self.append(item)
        return off

    def __iadd__(self, item):
        self.append(item)
        return self
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol,TCompactProtocol
from thrift.transport import TTransport
from hbase.Hbase import *

import struct

import ptvsd
ptvsd.settrace(None, ('0.0.0.0', 12345))
#ptvsd.wait_for_attach()

def encode(n):
   return struct.pack("i", n)

# Method for decoding ints with Thrift's string encoding
def decode(s):
   return int(s) if s.isdigit() else struct.unpack('i', s)[0]


   
class HBaseApi(object):
    def __init__(self,table='student',host='192.168.0.100',port=9090):
        self.table = table
        self.host = host
        self.port = port

        # Connect to HBase Thrift server
        self.transport = TSocket.TSocket(self.host, self.port)
        self.trans = TTransport.TBufferedTransport(self.transport)
        
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.trans)

        # Create and open the client connection
        self.client = Client(self.protocol)
        self.transport.open()

        # set type and field of column families
        self.set_column_families([bytes],['info'])
        self._build_column_families()


    def set_column_families(self,type_list,col_list=['info']):
        self.columnFamiliesType = type_list

        self.columnFamilies = col_list


    def _build_column_families(self):
        tables = self.client.getTableNames()
        if self.table not in tables:
            self.__create_table(self.table)

    def __create_table(self,table):
        columnFamilies = []
        for columnFamily in self.columnFamilies:
            name = ColumnDescriptor(name = columnFamily)
            columnFamilies.append(name)
        
        print(type(table),type(columnFamilies))

        self.client.createTable(table,columnFamilies)

    def __del__(self):
        self.transport.close()

    def del_table(self,table):
        self.client.disableTable(table)
        self.client.deleteTable(table)

    def getColumnDescriptors(self):
        return self.client.getColumnDescriptors(self.table)

    def put(self, rowKey, qualifier, value):
        mutations = []
        rowKey = rowKey.encode('utf-8')
        if isinstance(value, str):
            m_name = Mutation(column=(self.columnFamilies[0]+':'+qualifier).encode('utf8'), value=value.encode('utf8'))
        elif isinstance(value, int):
            m_name = Mutation(column=(self.columnFamilies[0]+':'+qualifier).encode('utf8'), value=encode(value))
        mutations.append(m_name)
        self.client.mutateRow(self.table, rowKey, mutations)

    def puts(self,rowKeys,qualifier,values):
        mutationsBatch = []
        if not isinstance(rowKeys,list):
            rowKeys = [rowKeys] * len(values)

        for i, value in enumerate(values):
            mutations = []
            
            if isinstance(value, str):
                m_name =Mutation(column=(self.columnFamilies[0]+':'+qualifier), value=value)
            elif isinstance(value, int):
                m_name =Mutation(column=(self.columnFamilies[0]+':'+qualifier), value=encode(value))
            mutations.append(m_name)
            mutationsBatch.append(BatchMutation(row = rowKeys[i],mutations=mutations))
        self.client.mutateRows(self.table, mutationsBatch)

    def getRow(self,row, qualifier='name'):
        row = self.client.getRow(self.table, row)
        for r in row:
            rd = {}
            row = r.row
            value = r.columns.get('info:'+qualifier).value
            rd[row] = value
        
            return rd

    def getRows(self, rows, qualifier='name'):
        res = []
        for r in rows:
            res.append(self.getRow(r,qualifier))
        return res

    def scanner(self, numRows=100, startRow='0002', stopRow='0002'):
        
        ss = 'info:name'
        scannerId = self.client.scannerOpenWithStop(self.table,startRow, stopRow,['info:age'])
        ret = []
        rowList = self.client.scannerGetList(scannerId, numRows)

        for r in rowList:
            rd = {}
            row = r.row
            value = (r.columns['info:age'].value)
            rd[row] = value
            ret.append(rd)

        return ret


from db.db_file_list import file_manager

def main():
    # ha = HBaseApi()
    # ha.put('0002','age','23')
    # rowKeys = [str(key) for key in range(10001,10010)]
    # values = ['fr'+str(val) for val in range(10001,10010)]
    # ha.puts(rowKeys,'name',values)
    # print(ha.scanner())
    # print(ha.getRow('0002','age'))
    # print(ha.getRows(rowKeys))
    file_manager.insert(3,'hello','13')
    file_manager.insert(3,'hello12','13')
    file_manager.remove(1)
    print(file_manager.file_list(3))

if __name__ == "__main__":
    main()



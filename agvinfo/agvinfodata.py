import xml.dom.minidom
from xml.etree import ElementTree
from  xml.etree.ElementTree import  Element, SubElement
from xml.dom.minidom import Document
from copy import deepcopy
import os,sys
import threading
from pynsp.logger import *

mutex_agvinfo = threading.RLock()

class proto_agvattribute_t:
    def __init__(self):
        self.name = ''
        self.describe = ''

class agvinfo_t:
    def __init__(self):
        self.vhid=0
        self.vhtype=0
        self.inet=''
        self.mtport=0
        self.shport=0
        self.ftsport=0
        self.hwaddr=''
        self.status=0
        self.attrs=[]

    def __str__(self):
        return 'vhid={} vhtype={} endpoint={}:{} hwaddr={} mtport={}'.format(self.vhid, self.vhtype, self.inet, self.shport, self.hwaddr,self.mtport)

    __repr__ = __str__

dict_xml_agvinfo=[]

def load_agvinfo_xml():
    path = sys.path[0]
    path = path + '/' + 'agv_info.xml'
    try:
        getTree = ElementTree.parse(path)
    except IOError:
        Logger().get_logger().error('Error:load_agvinfo_xml can not find agv_info.xml.')
        return
    except xml.etree.ElementTree.ParseError:
        Logger().get_logger().error('parse error. maybe no element existed.')
        return

    root = getTree.getroot()
    node = root.find('agvs')
    agvs=node.findall('agv')
    for agv in agvs:
        agvinfos = agvinfo_t()
        for child in agv.attrib:
            if child== 'id':
                agvinfos.vhid = int(agv.attrib[child])
            elif child=='type':
                agvinfos.vhtype=int(agv.attrib[child])
            elif child=='ip':
                agvinfos.inet=agv.attrib[child]
            elif child == 'port':
                agvinfos.mtport = int(agv.attrib[child])
            elif child=='shell_port':
                agvinfos.shport=int(agv.attrib[child])
            elif child=='fts_port':
                agvinfos.ftsport=int(agv.attrib[child])
            elif child=='status':
                agvinfos.status=int(agv.attrib[child])
            elif child=='mac_addr':
                agvinfos.hwaddr=agv.attrib[child]
            else:
                attr = proto_agvattribute_t()
                attr.describe = agv.attrib[child]
                attr.name = child
                agvinfos.attrs.append(attr)

        dict_xml_agvinfo.append(agvinfos)

def update_agvinfo(agvinfo):
    Logger().get_logger().info('updata write_xml id {}. ip{} port{} shell_port {}'.format(agvinfo.vhid,agvinfo.inet,agvinfo.mtport,agvinfo.shport))
    #print(agvinfo)
    flag=0
    for index in range(len(dict_xml_agvinfo)):
        if int(dict_xml_agvinfo[index].vhid)==agvinfo.vhid:
            dict_xml_agvinfo[index]=agvinfo
            change_agvinfo_xml(agvinfo)
            flag=1
            break
    if flag==0:
        add_agvinfo_xml(agvinfo)
        dict_xml_agvinfo.append(agvinfo)

def set_agvinfo(agvinfo_list):
    global dict_xml_agvinfo
    mutex_agvinfo.acquire()
    dict_xml_agvinfo = deepcopy(agvinfo_list)
    mutex_agvinfo.release()

def get_agvinfo()->list:
    global dict_xml_agvinfo
    agvinfo_dict = []
    mutex_agvinfo.acquire()
    agvinfo_dict = deepcopy(dict_xml_agvinfo)
    mutex_agvinfo.release()
    return agvinfo_dict
    
def change_agvinfo_xml(agvinfo):
    path = sys.path[0]
    path = path + '/' + 'agv_info.xml'
    try:
        updateTree = ElementTree.parse(path)
    except IOError:
        Logger().get_logger().error('Error:change_agvinfo_xml can not find agv_info.xml')
        return

    root = updateTree.getroot()
    node = root.find('agvs')
    agvs=node.findall('agv')
    for agv in agvs:
        if int(agv.get('id')) == agvinfo.vhid:
            agv.set('id', str(agvinfo.vhid))
            agv.set('type', str(agvinfo.vhtype))
            agv.set('ip', str(agvinfo.inet))
            agv.set('mac_addr', str(agvinfo.hwaddr))
            agv.set('port', str(agvinfo.mtport))
            agv.set('shell_port', str(agvinfo.shport))
            agv.set('fts_port', str(agvinfo.ftsport))
            agv.set('status', str(agvinfo.status))
            for i in range(len(agvinfo.attrs)):
                agv.set(agvinfo.attrs[i].name, agvinfo.attrs[i].describe)

    updateTree.write(path)

def add_agvinfo_xml(agvinfo):
    path = sys.path[0]
    path = path + '/' + 'agv_info.xml'
    try:
        updateTree = ElementTree.parse(path)
    except IOError:
        Logger().get_logger().error('Error:add_agvinfo_xml can not find agv_info.xml filed')
        new_agvinfo_xml(agvinfo,path)
        return
    except xml.etree.ElementTree.ParseError:
        Logger().get_logger().error('parse error. maybe no element existed')
        new_agvinfo_xml(agvinfo,path)
        return
    root = updateTree.getroot()
    node = root.find('agvs')
    newEle = ElementTree.Element('agv')
    newEle.attrib = {"id": str(agvinfo.vhid), "type":str(agvinfo.vhtype),'ip':str(agvinfo.inet),
                    'mac_addr':str(agvinfo.hwaddr),'port':str(agvinfo.mtport),
                     'shell_port': str(agvinfo.shport),'fts_port':str(agvinfo.ftsport),'status':str(agvinfo.status)}
    for i in range(len(agvinfo.attrs)):
        newEle.attrib[agvinfo.attrs[i].name]=str(agvinfo.attrs[i].describe)

    node.append(newEle)
    updateTree._setroot(root)
    updateTree.write(path)


def new_agvinfo_xml(agvinfo,path):

    root=Element('agv_info')
    agvsEle=SubElement(root,'agvs')
    updateTree=xml.etree.ElementTree.ElementTree(root)
    #updateTree=ElementTree(root)

    head=SubElement(agvsEle,'agv')
    head.attrib = {"id": str(agvinfo.vhid), "type": str(agvinfo.vhtype), 'ip': str(agvinfo.inet),
                     'mac_addr': str(agvinfo.hwaddr), 'port': str(agvinfo.mtport),
                     'shell_port': str(agvinfo.shport), 'fts_port': str(agvinfo.ftsport), 'status': str(agvinfo.status)}
    for i in range(len(agvinfo.attrs)):
        head.attrib[agvinfo.attrs[i].name] = str(agvinfo.attrs[i].describe)

    updateTree.write(path)

def creat_agvinfo_xml(path,agvinfo):
    pass

if __name__ == "__main__":
    #t=tcp_manage()
    #t.load_agvinfo_xml()
    load_agvinfo_xml()

    for i in range(len(dict_xml_agvinfo)):
        Logger().get_logger().info('dict_xml_agvinfo vhid ={}.'.format(dict_xml_agvinfo[i].vhid))

    t=agvinfo_t()
    t.vhid=11
    t.vhtype=2
    t.shport=101
    t.mtport=102
    t.ftsport=103
    t.inet='10.10.10.10'
    tt=[]
    tt.append(t)
    #dict_xml_agvinfo=tt
    #write_agvinfo_xml()
    update_agvinfo(t)
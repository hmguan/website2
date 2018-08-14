#!/usr/bin/python3
import shutil
import os
import xml.etree.ElementTree as ET
#import ptvsd

#ptvsd.settrace(None, ('0.0.0.0', 12345))
#ptvsd.wait_for_attach()


def find_target(root,tar_node):
    for child in root:
       if tar_node==child.tag:
           return child
    return None


#修改属性
def property_mode(index,element,proerty,value):
    print(element,proerty,value)
    tree = ET.parse(element[0])
    root = tree.getroot()
    
    # 路径 根节点无需循环
    loop_num = len(element)-2
    for i in range(loop_num):
        root = find_target(root,element[i+2])
        if None == root:
            print('index:%d,can not find target node:%s'%(index,element[i+2]))    
            return
    

    root.set(proerty, value)

    try:
        tree.write(element[0])
    except Exception as e:
        print(str(e))
    
    return -1 

 # 修改元素
def element_mode(index,element,value):
    print(element,value)

    tree = ET.parse(element[0])
    root = tree.getroot()
    
    # 路径 根节点无需循环
    loop_num = len(element)-2
    for i in range(loop_num):
        root = find_target(root,element[i+2])
        if None == root:
            print('index:%d,can not find target node:%s'%(index,element[i+2]))    
            return -1
    
    root.text = value

    try:
        tree.write(element[0])
    except Exception as e:
        print(str(e))
    
    return -1 

def restore_file(index,path):
    backup_path = path + '.backup'
    if False==os.path.exists(backup_path):
        print('restore file is not exist')
        return -1
    
    if False==os.path.exists(path):
        print('original file is not exist')
        return -1
    
    #移除原始文件
    os.remove(path)
    #还原备份文件
    os.rename(backup_path,path)
    return 0


def update_file(index,parms):
    if False==os.path.exists(parms[0]):
        print('target file is not exist')
        return 
    
    #1.检查还原
    if 1==len(parms):
        return restore_file(index,parms[0])
    
    #2.备份,覆盖旧备份
    shutil.copy(parms[0],parms[0]+'.backup')

    #3.修改文件 &代表修改节的属性
    last_parm = parms[len(parms)-1]
    pos = last_parm.find('&')
    if pos<0:
        element_mode(index,parms[0:len(parms)-1],parms[len(parms)-1])
    else:
        property_mode(index,parms[0:len(parms)-1],last_parm[0:pos],last_parm[pos+1:])
    

    
def main():
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path= dir_path+'/update_xml.txt'

    if False==os.path.exists(file_path):
        print('update_xml config file is not exist')
        return
    
    file_object = open(file_path,'r')
    try:
        index=-1 
        for line in file_object:
            index = index+1
            parms = line.split()
            if len(parms)<3 and 1!=len(parms):
                print('index:%d,parms size is less than 3,actual is %d'%(index,len(parms)))
                continue
            
            print('index:%d,'%(index),parms)
            update_file(index,parms)
    finally:
        file_object.close()


if __name__ == '__main__':
    main()
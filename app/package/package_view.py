import flask
import json
from flask import jsonify
from app.main.mainview import base_event
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from flask import jsonify
from flask import Flask, request
from db.db_users import user
from db.db_package import package_manager
from configuration import config
from agvshell.shell_api import push_file_to_remote
from agvshell.transfer_file_types import *
import errtypes
import os

class package_view(base_event):
    def __init__(self):
        super(package_view,self).__init__()
        self.regist_event('event_package_upload','event_package_update','event_package_remove','event_packages','event_robot_upgrade','event_download_files')
        
    def flask_recvdata(self,requst_obj):
        data = requst_obj.get_data()
        json_data = json.loads(data.decode('utf-8'))
        event = json_data['event']

        if 'event_package_update'==event:
            if 'package_id' not in json_data or 'remark' not in json_data: 
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament, 'msg': '参数错误'})

            retval = package_manager.update(json_data['package_id'],json_data['remark'])
            if retval<0:
                return jsonify( {'code': errtypes.HttpResponseCode_ServerError, 'msg': '更新失败'})
            ret = {'code': 0, 'msg': '更新成功'}
        
        if 'event_package_remove'==event:
            if 'package_id' not in json_data : 
                return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': '参数错误'}

            retval = package_manager.remove(json_data['package_id'])
            if retval<0:
                return jsonify({'code': errtypes.HttpResponseCode_ServerError, 'msg': '删除失败'})
            ret = {'code': 0, 'msg': '删除成功'}

        if 'event_packages'==event:
            retval = package_manager.packages(json_data['user_id'])
            
            list_package=[]
            for index, value in enumerate(retval):
                tmp={}
                tmp['id']= value.id
                tmp['user_name']= value.user.username
                tmp['version']= value.version
                tmp['package_name'] = value.package_name
                tmp['time']= value.time.strftime("%Y/%m/%d %H:%M:%S") 
                tmp['remarks'] = value.remarks
                list_package.append(tmp)
            ret = {'code':0,'msg':'查询成功','data':{'users':list_package}}
        elif 'event_robot_upgrade' == event:
            
            package_id = json_data.get('package_id')
            robot_list = json_data.get('robot_list')
            user_id = json_data.get('user_id')
            if type(package_id) != int or robot_list is None or type(user_id) != int:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament })
            try:
                retval = package_manager.query_packages(package_id)
                if retval is None:
                    return jsonify({'code': errtypes.HttpResponseCode_Failed, 'msg': errtypes.HttpResponseMsg_Failed })

                user_name = retval.user.username
                package_name = retval.package_name
                file_path = config.ROOTDIR +user_name +config.PATCHFOLDER + package_name
                if os.path.exists(file_path) == False:
                    return jsonify({'code': errtypes.HttpResponseCode_InvaildPath, 'msg': errtypes.HttpResponseMsg_InvaildPath })
                
                err_robots = None
                task_list,err_robots = push_file_to_remote(user_id,robot_list,file_path,FILE_TYPE_A_UPGRADE,package_id)

                ret = {'code': 0,'msg':errtypes.HttpResponseMsg_Normal,'transfer_list':task_list,'error_robots':err_robots}
            except Exception as e:
                ret = {'code': errtypes.HttpResponseCode_ServerError,'msg':str(e)}
        elif 'event_download_files' == event:
            user_id = json_data.get('user_id')
            package_name = json_data.get('package_name')
            user_name = user.query_name_by_id(user_id)
            if user_name is None:
                return jsonify({'code': errtypes.HttpResponseCode_UserNotExisted,'msg':'用户不存在'})
            file_path = config.ROOTDIR +user_name +config.PATCHFOLDER + package_name
            if os.path.exists(file_path) == False:
                return jsonify({'code': errtypes.HttpResponseCode_NOFILE,'msg':'文件不存在'''})
            if file_path[0] == '.':
                file_path = file_path[1:]
            ret = {'code': 0,'msg':errtypes.HttpResponseMsg_Normal,'file_path':file_path}
        return jsonify(ret)
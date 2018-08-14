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
from configuration import get_config_path
from agvshell.shell_api import push_file_to_remote
from agvshell.transfer_file_types import *
import errtypes
import httpRequestCode
import os
from configuration import config


class package_view(base_event):
    def __init__(self):
        super(package_view,self).__init__()
        self.regist_event('event_package_update','event_package_remove','event_package_list')
        
    def flask_recvdata(self,json_data):
        event = json_data['event']
        if 'event_package_update'==event:
            if 'package_id' not in json_data or 'remark' not in json_data: 
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament})
            if 'login_id' not in json_data or  type(json_data['login_id'])!=int:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament})

            retval = package_manager.update(json_data['package_id'],json_data['remark'])
            if -1==retval:
                return jsonify( {'code': errtypes.HttpResponseCode_NOEXISTPackage, 'msg': errtypes.HttpResponseCodeMsg_NOEXISTPackage})
            if -2==retval:
                return jsonify( {'code': errtypes.HttpResponseCode_Sqlerror, 'msg': errtypes.HttpResponseCode_Sqlerror})
            ret = {'code': 0, 'msg': 'success'}
        
        if 'event_package_remove'==event:
            if 'package_id' not in json_data : 
                return {'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament}

            retval = package_manager.remove(json_data['package_id'])
            if -1==retval:
                return jsonify( {'code': errtypes.HttpResponseCode_NOEXISTPackage, 'msg': errtypes.HttpResponseCodeMsg_NOEXISTPackage})
            if -2==retval:
                return jsonify( {'code': errtypes.HttpResponseCode_FailedRemoveFile, 'msg': errtypes.HttpResponseCodeMsg_FailedRemoveFile})
            if -3==retval:
                return jsonify( {'code': errtypes.HttpResponseCode_Sqlerror, 'msg': errtypes.HttpResponseCode_Sqlerror})
            if -4==retval:
                return jsonify({'code': errtypes.HttpResponseCode_FileBusy, 'msg': errtypes.HttpResponseMsg_FileBusy })
            ret = {'code': 0, 'msg': 'success'}

        if 'event_package_list'==event:
            if 'login_id' not in json_data or  type(json_data['login_id'])!=int:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament})

            retval = package_manager.packages(json_data['login_id'])
            if -1==retval:
                return jsonify( {'code': errtypes.HttpResponseCode_Sqlerror, 'msg': errtypes.HttpResponseCode_Sqlerror})

            list_package=[]
            for index, value in enumerate(retval):
                tmp={}
                tmp['package_id']= value.id
                tmp['user_name']= value.user.username
                tmp['version']= value.version
                tmp['package_name'] = value.package_name
                tmp['time']= value.time.strftime("%Y/%m/%d %H:%M:%S") 
                tmp['remarks'] = value.remarks
                list_package.append(tmp)
            ret = {'code':0,'msg':'success','data':{'users':list_package}}        
        return jsonify(ret)
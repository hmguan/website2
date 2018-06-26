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
import errtypes


class package_view(base_event):
    def __init__(self):
        super(package_view,self).__init__()
        self.regist_event('event_package_upload','event_package_update','event_package_remove','event_packages')
        
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
                tmp['time']= value.time
                tmp['remarks'] = value.remarks
                list_package.append(tmp)
            ret = {'code':0,'msg':'查询成功','data':{'users':list_package}}

        return jsonify(ret)
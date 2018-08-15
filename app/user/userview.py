import flask
import json
from flask import jsonify
from app.main.mainview import base_event
from .user_service_agant import users_center
import errtypes


class userview(base_event):
    def __init__(self):
        super(userview,self).__init__()
        self.regist_event('event_login','event_logout','event_register_user','event_update_pwd',
        'event_remove_user','event_users','event_reset_pwd','event_alter_permission','event_group_alias','event_query_alias')

    def flask_recvdata(self,json_data):
        event = json_data['event']
    
        if 'event_register_user'==event:
            if 'login_id' not in json_data  or type(json_data['login_id']) !=int:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            if 'user_name' not in json_data  or type(json_data['user_name']) !=str:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            if 'password' not in json_data  or type(json_data['password']) !=str:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            if 'permission' not in json_data or type(json_data['permission']) !=str:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            ret = users_center.register_user(json_data['login_id'],json_data['user_name'], json_data['password'],json_data['permission'])
        
        if 'event_update_pwd'==event:
            if 'login_id' not in json_data  or type(json_data['login_id']) !=int:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            if 'old_password' not in json_data or type(json_data['old_password']) !=str:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            if 'new_password' not in json_data or type(json_data['new_password']) !=str:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            ret = users_center.update_pwd(json_data['login_id'],json_data['old_password'],json_data['new_password'])
        
        if 'event_remove_user'==event:
            if 'login_id' not in json_data  or type(json_data['login_id']) !=int:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            if 'target_id' not in json_data  or type(json_data['target_id']) !=int:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            ret = users_center.remove_user(json_data['login_id'],json_data['target_id'])
        
        if 'event_users'==event:
            if 'login_id' not in json_data  or type(json_data['login_id']) !=int:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            ret = users_center.users(json_data['login_id'])
            
        
        if 'event_login'==event:
           
            if 'login_token' in json_data:
                if type(json_data['login_token']) !=str:
                    return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
                if 'uuid' not in json_data or type(json_data['uuid']) !=str:
                    return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}

                ret =  users_center.verify_auth_token(json_data['login_token'],json_data['uuid'])
                return jsonify(ret)
            
            if 'user_name' not in json_data  or type(json_data['user_name']) !=str:
                    return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            if 'password' not in json_data  or type(json_data['password']) !=str:
                    return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            
            ret = users_center.user_login(json_data['user_name'], json_data['password'])
        
        if 'event_logout'==event:
            if 'login_id' not in json_data  or type(json_data['login_id']) !=int:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            ret = users_center.user_logout(json_data['login_id'])
        if 'event_reset_pwd'==event:
            if 'login_id' not in json_data  or type(json_data['login_id']) !=int:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            if 'target_id' not in json_data  or type(json_data['target_id']) !=int:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            ret = users_center.reset_pwd(json_data['login_id'],json_data['target_id'])
        
        if 'event_alter_permission'==event:
            if 'login_id' not in json_data or type(json_data['login_id']) !=int:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            if 'target_id' not in json_data or type(json_data['target_id']) !=int:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            if 'permission' not in json_data or type(json_data['permission']) !=str:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            ret = users_center.reset_permission(json_data['login_id'],json_data['target_id'],json_data['permission'])

        if 'event_group_alias'==event:
            if 'login_id' not in json_data or type(json_data['login_id']) !=int:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            if 'group_name' not in json_data or type(json_data['group_name']) !=str:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            if 'alias' not in json_data  or type(json_data['alias']) !=str:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            ret = users_center.update_group_alias(json_data['login_id'], json_data['group_name'],json_data['alias'])
        
        if  'event_query_alias'==event:
            if 'login_id' not in json_data  or type(json_data['login_id']) !=int:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            if 'group_name' not in json_data  or type(json_data['group_name']) !=str:
                return {'code':errtypes.HttpResponseCode_InvaildParament,'msg':errtypes.HttpResponseMsg_InvaildParament}
            ret = users_center.group_alias(json_data['login_id'], json_data['group_name'])
        return jsonify(ret)
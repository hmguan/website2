import flask
import json
from flask import jsonify
from app.main.mainview import base_event
from . import user_manager

users_center = user_manager.user_manager()

class userview(base_event):
    def __init__(self):
        super(userview,self).__init__()
        self.regist_event('event_login','event_logout','event_register_user','event_update_pwd',
        'event_remove_user','event_users','event_reset_pwd','event_alter_permission','event_group_alias','event_query_alias')

    def flask_recvdata(self,requst_obj):
        data = requst_obj.get_data()
        json_data = json.loads(data.decode('utf-8'))
        event = json_data['event']
    
        if 'event_register_user'==event:
            ret = users_center.register_user(json_data['user_name'], json_data['password'],json_data['permission'])
        if 'event_update_pwd'==event:
            ret = users_center.update_pwd(json_data['user_id'],json_data['old_password'],json_data['new_password']) 
        if 'event_remove_user'==event:
            ret = users_center.remove_user(json_data['user_id'])
        if 'event_users'==event:
            ret = users_center.users()
        if 'event_login'==event:
            if 'token' in json_data:
                ret =  users_center.verify_auth_token(json_data['token'],json_data['uuid'])
                return jsonify(ret)
            ret = users_center.user_login(json_data['user_name'], json_data['password'])
        if 'event_logout'==event:
            ret = users_center.user_logout(json_data['user_id'])
        if 'event_reset_pwd'==event:
            ret = users_center.reset_pwd(json_data['user_id'])
        if 'event_alter_permission'==event:
            ret = users_center.reset_permission(json_data['user_id'],json_data['permission'])
        if 'event_group_alias'==event:
            ret = users_center.update_group_alias(json_data['user_id'], json_data['group_name'],json_data['alias'])
        if  'event_query_alias'==event:
            ret = users_center.group_alias(json_data['user_id'], json_data['group_name'])
        return jsonify(ret)
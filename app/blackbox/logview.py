from app.main.mainview import base_event
import json
from flask import jsonify
from black_box.black_box import *
from db.db_blackbox import blackbox_manager

class logview(base_event):
    def __init__(self):
        super(logview,self).__init__()
        self.regist_event('get_log_types','send_log_condition','cancle_get_log','event_bk_temps_insert','event_bk_temps','event_bk_temps_remove')
        pass

    def flask_recvdata(self,requst_obj):
        data = requst_obj.get_data()
        json_data = json.loads(data.decode('utf-8'))
        event = json_data['event']
        if 'get_log_types' == event:
            type_list=get_agv_types(json_data.get('robot_id'))
            ret={'code':0,'msg':errtypes.HttpResponseMsg_Normal,'data':type_list}
            return jsonify(ret)

        if 'send_log_condition' == event:
            robot_list=json_data['robot_id']
            task_id=send_log_condition(robot_list,json_data['user_id'],json_data.get('start_time'),json_data.get('end_time'),{'motion_template','agv_shell'},json_data['name'])#json_data.get('type_list')
            ret={'code': 0,'msg':errtypes.HttpResponseMsg_Normal,'task_id':task_id}
            return jsonify(ret)

        if 'cancle_get_log'==event:
            back=cancle_get_log(json_data['task_id'])
            ret={'code':0,'msg':errtypes.HttpResponseMsg_Normal,'result':back}
            return jsonify(ret)

        if 'event_bk_temps_insert'==event:
            ret = blackbox_manager.insert_temps(json_data['user_id'],json_data.get('temps_types'),json_data.get('others'),json_data.get('time'))
            if ret<0:
                return jsonify({'code': errtypes.HttpResponseCode_ServerError, 'msg': '添加失败'})
            
            return jsonify({'code': 0, 'msg': '添加成功'})

        if 'event_bk_temps_remove'==event:
            ret = blackbox_manager.remove_temps(json_data['user_id'])
            if ret<0:
                return jsonify({'code': errtypes.HttpResponseCode_ServerError, 'msg': '删除失败'})
            
            return jsonify({'code': 0, 'msg': '删除成功'})
        
        if 'event_bk_temps'==event:
            ret = blackbox_manager.temps(json_data['temps_id'])
            if ret<0:
                return jsonify({'code': errtypes.HttpResponseCode_ServerError, 'msg': '查询失败'})
            
            return jsonify({'code': 0, 'msg': '查询成功'})
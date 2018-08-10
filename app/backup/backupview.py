from app.main.mainview import base_event
import json
from flask import jsonify
from backup.backup_api import *
from db.db_blackbox import blackbox_manager


class backupview(base_event):
    def __init__(self):
        super(backupview, self).__init__()
        self.regist_event('get_log_types', 'send_log_condition', 'cancle_get_log', 'event_bk_temps_insert',
                          'event_bk_temps_remove', 'event_bk_temps',
                          'get_executing_log', 'delete_log', 'get_log_list', 'download_log')
        pass

    def flask_recvdata(self, json_data):

        event = json_data['event']
        if 'get_log_types' == event:
            robot_id = json_data['robot_id']
            if robot_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            type_list = get_agv_types(robot_id)
            ret = {'code': 0, 'msg': errtypes.HttpResponseMsg_Normal, 'data': type_list}
            return jsonify(ret)

        if 'send_log_condition' == event:
            robot_id = json_data['robot_id']
            if robot_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            task_id = send_log_condition(robot_id, int(json_data['user_id']), json_data.get('start_time'),
                                      json_data.get('end_time'), json_data.get('type_list'),
                                      json_data['name'])  # ['agv_shell','nshost']
            if task_id >0:
                return jsonify({'code': 0,'msg':errtypes.HttpResponseMsg_Normal,'task_id':task_id})
            elif task_id<=0:
                return jsonify({'code': errtypes.HttpResponseCode_Failed, 'msg': errtypes.HttpResponseMsg_Failed,'tasl_id':task_id})

        if 'cancle_get_log' == event:
            task_id=json_data['task_id']
            if type(task_id) != int or task_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            back = cancel_get_log(task_id)
            ret = {'code': 0, 'msg': errtypes.HttpResponseMsg_Normal, 'result': back}
            return jsonify(ret)

        if 'event_bk_temps_insert' == event:
            user_id=json_data['user_id']
            if type(user_id) != int or user_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            ret = blackbox_manager.insert_temps(user_id, json_data['name'], json_data.get('temps_types'),
                                                json_data.get('others'))
            if ret < 0:
                return jsonify({'code': errtypes.HttpResponseCode_ServerError, 'msg': '添加失败'})

            return jsonify({'code': 0, 'msg': '添加成功'})

        if 'event_bk_temps_remove' == event:
            temps_id=json_data['temps_id']
            if type(temps_id) != int or temps_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            ret = blackbox_manager.remove_temps(temps_id)
            if ret < 0:
                return jsonify({'code': errtypes.HttpResponseCode_ServerError, 'msg': '删除失败'})

            return jsonify({'code': 0, 'msg': '删除成功'})

        if 'event_bk_temps' == event:
            user_id=json_data['user_id']
            if type(user_id) != int or user_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            ret = blackbox_manager.temps(user_id)

            list_temps = []
            for index, value in enumerate(ret):
                tmp = {}
                tmp['id'] = value.id
                tmp['name'] = value.name
                tmp['temps_types'] = value.temps_types
                tmp['others'] = value.others
                tmp['time'] = value.time.strftime("%Y/%m/%d %H:%M:%S")
                list_temps.append(tmp)
            ret = {'code': 0, 'msg': '查询成功', 'data': {'temps': list_temps}}
            return jsonify(ret)

        if 'get_executing_log' == event:
            user_id=json_data['user_id']
            if type(user_id) != int or user_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            log_name, task_id, step = get_executing_log(user_id)
            ret = {'code': 0, 'msg': errtypes.HttpResponseCode_Normal, 'log_name': log_name, 'task_id': task_id,
                   'step': step}
            return jsonify(ret)

        if 'delete_log' == event:
            user_id=json_data['user_id']
            if type(user_id) != int or user_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            log_name = json_data['log_name']
            ret = delete_log(user_id, log_name)
            if ret < 0:
                return jsonify({'code': errtypes.HttpResponseCode_Failed, 'msg': errtypes.HttpResponseMsg_Failed})
            return jsonify({'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal})

        if 'get_log_list' == event:
            user_id=json_data['user_id']
            if type(user_id) != int or user_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            log_list = get_log_list(user_id)
            return jsonify({'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal,
                            'log_list': log_list})

        if 'download_log' == event:
            user_id=json_data['user_id']
            if type(user_id) != int or user_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            log_name = json_data['log_name']
            path = download_log(user_id, log_name)
            return jsonify(
                {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'path': path})

from app.main.mainview import base_event
import json
from flask import jsonify
from backup.backup_api import *
from db.db_blackbox import blackbox_manager
from db.db_file_list import file_manager


class backupview(base_event):
    def __init__(self):
        super(backupview, self).__init__()
        self.regist_event('get_log_types', 'send_log_condition', 'cancel_get_log', 'event_bk_temps_insert',
                          'event_bk_temps_remove', 'event_bk_temps',
                          'get_executing_log', 'delete_log', 'get_log_list')
        pass

    def flask_recvdata(self, json_data):

        event = json_data['event']
        if 'get_log_types' == event:
            robot_id = json_data['robot_id']
            if robot_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            type_list = get_agv_types(robot_id)
            ret = {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'data': type_list}
            return jsonify(ret)

        if 'send_log_condition' == event:
            robot_id = json_data['robot_id']
            user_id = json_data['login_id']
            time_type=json_data['time_select_type']
            if type(robot_id) != list or len(robot_id)==0 or type(user_id) != int or user_id is None or type(time_type)!=int or time_type is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})

            task_id = send_log_condition(robot_id, int(user_id), json_data.get('start_time'),
                                         json_data.get('end_time'),json_data.get('is_latest_time'),
                                         json_data.get('time_select_type'), json_data.get('type_list'),
                                         json_data['name'])  # ['agv_shell','nshost']
            if task_id >0:
                return jsonify({'code': errtypes.HttpResponseCode_Normal,'msg':errtypes.HttpResponseMsg_Normal,'task_id':task_id})
            elif task_id==-1:
                return jsonify({'code': errtypes.HttpResponseCode_BlackboxSendFailed, 'msg': errtypes.HttpResponseMsg_BlackboxSendFailed,'tasl_id':task_id})
            elif task_id==-2:
                return jsonify({'code': errtypes.HttpResponseCode_BlackboxReTask, 'msg': errtypes.HttpResponseMsg_BlackboxReTask,
                                'tasl_id': task_id})

        if 'cancel_get_log' == event:
            task_id=json_data['task_id']
            if type(task_id) != int or task_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            back = cancel_get_log(task_id)
            if back<0:#任务不存在
                return jsonify({'code': errtypes.HttpResponseCode_BlackboxNoTask, 'msg': errtypes.HttpResponseMsg_BlackboxNoTask, 'result': back})
            elif back==0:
                return jsonify({'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'result': back})
            elif back==1:#正在后台压缩，等待取消
                return jsonify({'code': errtypes.HttpResponseCode_BlackboxWaitTar, 'msg': errtypes.HttpResponseMsg_BlackboxWaitTar, 'result': back})

        if 'event_bk_temps_insert' == event:
            login_id=json_data['login_id']
            if type(login_id) != int or login_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            ret = blackbox_manager.insert_temps(login_id, json_data['name'], json_data.get('temps_types'),
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
            login_id=json_data['login_id']
            if type(login_id) != int or login_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            ret = blackbox_manager.temps(login_id)

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
            user_id=json_data['login_id']
            if type(user_id) != int or user_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            log_name, task_id, step = get_executing_log(user_id)
            if task_id==-1:
                return jsonify({'code': errtypes.HttpResponseCode_BlackboxNoTask, 'msg': errtypes.HttpResponseMsg_BlackboxNoTask,
                       'log_name': log_name, 'task_id': task_id,'step': step})
            return jsonify({'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'log_name': log_name, 'task_id': task_id,
                   'step': step})

        if 'delete_log' == event:
            user_id=json_data['login_id']
            file_id = json_data['file_id']
            if type(user_id) != int or user_id is None or type(file_id)!=int or file_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            # log_name = json_data['log_name']
            # ret = delete_log(user_id, log_name)
            # if ret < 0:
            #     return jsonify({'code': errtypes.HttpResponseCode_Failed, 'msg': errtypes.HttpResponseMsg_Failed})
            # return jsonify({'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal})

            ret=file_manager.remove(file_id)
            if ret==-2:
                return jsonify({'code': errtypes.HttpResponseCode_BlackboxDeleteFailed, 'msg': errtypes.HttpResponseMsg_BlackboxDeleteFailed,'data': ret})
            elif ret==-1:
                return jsonify({'code': errtypes.HttpResponseCode_BlackboxDbNoFile, 'msg': errtypes.HttpResponseMsg_BlackboxDbNoFile, 'data': ret})
            else:
                return jsonify({'code': errtypes.HttpResponseCode_Normal,'msg': errtypes.HttpResponseMsg_Normal, 'data': ret})

        if 'get_log_list' == event:
            user_id=json_data['login_id']
            if type(user_id) != int or user_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            # log_list = get_log_list(user_id)
            # return jsonify({'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal,
            #                 'log_list': log_list})
            ret_list=file_manager.file_list(user_id)
            log_list=list()
            for i in range(len(ret_list)):
                log_item = dict()
                print('ret_list',i,ret_list[i].file_name)
                log_item['file_id']=ret_list[i].id
                log_item['file_name'] = ret_list[i].file_name
                log_item['user_id'] = ret_list[i].user_id
                log_item['file_size'] = ret_list[i].file_size
                log_item['time'] = ret_list[i].time.strftime("%Y/%m/%d %H:%M:%S")
                log_list.append(log_item)
            return jsonify({'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal,'log_list': log_list})

        if 'download_log' == event:
            login_id=json_data['login_id']
            if type(login_id) != int or login_id is None:
                return jsonify({'code': errtypes.HttpResponseCode_InvaildParament,'msg': errtypes.HttpResponseMsg_InvaildParament, 'data': ''})
            log_name = json_data['log_name']
            path = download_log(login_id, log_name)
            return jsonify(
                {'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'path': path})

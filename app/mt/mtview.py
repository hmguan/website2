import flask
import json
from flask import jsonify,request,session,render_template
from agvmt.mt_api import get_nav_data,get_veh_data,get_ope_data,get_opt_data,get_var_list,get_vars_data,clear_error,set_stop_emergency,get_robots_status
from ..main.mainview import base_event
from agvmt.mtproto import viewtype,view_data
import errtypes

class mt_view(base_event):
    def __init__(self):
        super(mt_view, self).__init__()
        self.regist_event('load_navigation', 'load_vehicle','load_operation','load_optpar','load_varlist','load_vardata','clear_error','stop_emergency','load_error_status')
        pass

    def flask_recvdata(self,requst_obj):
        data = requst_obj.get_data()
        json_data = json.loads(data.decode('utf-8'))
        event = json_data['event']
        print('user flaks', event)
        print('--------------json_data:', json_data)

        if 'load_vehicle'==event:
            robot_id = json_data['robot_id']
            if len(robot_id) == 0:
                return (render_template('templates/vehicle.html', data=view_data.vehicle_t()))#jsonify({'code':errtypes.HttpResponseCode_RequstErr})
            info = get_veh_data(int(robot_id))
            return (render_template('templates/vehicle.html', data=info))
        elif 'load_navigation' == event:
            robot_id = json_data['robot_id']
            if len(robot_id) == 0:
                return (render_template('templates/navigation.html', data=view_data.navigation_t()))
            info = get_nav_data(int(robot_id))
            return (render_template('templates/navigation.html', data=info))
        elif 'load_operation'==event:
            robot_id = json_data['robot_id']
            if len(robot_id) == 0:
                return (render_template('templates/operation.html', data=view_data.operation_t()))
            info = get_ope_data(int(robot_id))
            return (render_template('templates/operation.html', data=info))
        elif 'load_optpar'==event:
            robot_id = json_data['robot_id']
            if len(robot_id) == 0:
                return (render_template('templates/optpar.html', data=view_data.optpar_t()))
            info = get_opt_data(int(robot_id))
            return (render_template('templates/optpar.html', data=info))
        elif 'load_varlist'==event:
            robot_id = json_data['robot_id']
            if len(robot_id) == 0:
                return jsonify({'code':errtypes.HttpResponseCode_RequstErr})
            info = get_var_list(int(robot_id))
            print('-------------------------load_varlist:', len(info))
            var_view = []#[{0:{1:'a'}},{2:{3:'b'}},{4:{5:'c'}}]
            view=dict()
            for iter in info:
                 view[int(iter.var_id)] = {int(iter.var_type): viewtype.typeDict[int(iter.var_type)]}
                 var_view.append({int(iter.var_id):{int(iter.var_type): viewtype.typeDict[int(iter.var_type)]}})

            return jsonify({'code': errtypes.HttpResponseCode_Normal,'msg': errtypes.HttpResponseMsg_Normal,'data':var_view})
        elif 'load_vardata'==event:
            robot_id = json_data['robot_id']
            var_id = json_data['data'][0]['var_id']
            type_id = json_data['data'][0]['type_id']

            if len(robot_id) == 0 or len(type_id)==0 or len(var_id)==0:
                return jsonify([{'result': 'error'}])
            info = get_vars_data(int(robot_id),int(var_id),int(type_id))
            return jsonify({'code': errtypes.HttpResponseCode_Normal,'msg': errtypes.HttpResponseMsg_Normal,'data':info})
        elif 'clear_error'==event:
            robot_list=json_data['robot_id']
            if len(robot_list)==0:
                return jsonify({'code':errtypes.HttpResponseCode_RequstErr, 'msg': errtypes.HttpResponseMsg_RequstErr, 'data': ''})
            clear_error(robot_list)
            return jsonify({'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'data': ''})
        elif 'stop_emergency'==event:
            robot_list=json_data['robot_id']
            if len(robot_list)==0:
                return jsonify({'code':errtypes.HttpResponseCode_RequstErr, 'msg': errtypes.HttpResponseMsg_RequstErr, 'data': ''})
            set_stop_emergency(robot_list)
            return jsonify({'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal, 'data': ''})
        elif 'load_error_status'==event:
            # robot_list=json_data['robot_id']
            # if len(robot_list)==0:
            #     return jsonify({'result','error'})
            info=get_robots_status()
            return jsonify({'code':errtypes.HttpResponseCode_Normal,'msg':errtypes.HttpResponseMsg_Normal,'data':info})


from .mtproto import viewtype,view_data,mthead

#根据类型，返回length
def get_var_read_length(type_id):
    if type_id == viewtype.kVarType_CanBus:
        can_data = view_data.var__can_device_t()
        return can_data.length()

    elif type_id == viewtype.kVarType_Elmo:
        elmo_data = view_data.var__elmo_t()
        return elmo_data.length()

    # elif type_id == viewtype.kVarType_Copley:
    #     pass
    elif type_id == viewtype.kVarType_DIO:
        dio_data = view_data.var__dio_t()
        return dio_data.length()

    elif type_id == viewtype.kVarType_Moons:
        moons_data = view_data.var__moons_t()
        return moons_data.length()

    elif type_id == viewtype.kVarType_AngleEncoder:
        angle_data = view_data.var__angle_encoder_t()
        return angle_data.length()

    elif type_id == viewtype.kVarType_SafetyProtec:
        safe_data=view_data.var__safety_t()
        return safe_data.length()

    elif type_id == viewtype.kVarType_Vehicle:
        vehi_data = view_data.vehicle_t()
        print('mt--length',vehi_data.length())
        return vehi_data.length()

    elif type_id == viewtype.kVarType_Navigation:
        nav_data = view_data.navigation_t()
        print('mt--length', nav_data.length())
        return nav_data.length()

    elif type_id == viewtype.kVarType_Operation:
        oper_data = view_data.operation_t()
        return oper_data.length()

    elif type_id == viewtype.kVarType_UserDefined:
        userdef_data=view_data.var__usrdef_buffer_t()
        return userdef_data.length()

    elif type_id == viewtype.kVarType_SWheel:
        swheel_data=view_data.var__swheel_t()
        return swheel_data.length()

    elif type_id == viewtype.kVarType_DWheel:
        dwheel_data=view_data.var__dwheel_t()
        return dwheel_data.length()

    elif type_id == viewtype.kVarType_SDDExtra:
        sdd_data=view_data.var__sdd_extra()
        return sdd_data.length()

    elif type_id == viewtype.kVarType_OperationTarget:
        optpar_data=view_data.optpar_t()
        return optpar_data.length()

    else:pass

#根据类型，返回存在的类型有效的list
def get_valid_list(var_list):
    valid_list=list()
    for id in var_list:
        if id.var_type == viewtype.kVarType_CanBus or id.var_type ==viewtype.kVarType_Elmo or \
                id.var_type == viewtype.kVarType_DIO or id.var_type == viewtype.kVarType_Moons or id.var_type == viewtype.kVarType_AngleEncoder or \
                id.var_type == viewtype.kVarType_SafetyProtec or id.var_type == viewtype.kVarType_Vehicle or id.var_type == viewtype.kVarType_Navigation or \
                id.var_type == viewtype.kVarType_Operation or id.var_type == viewtype.kVarType_UserDefined or id.var_type == viewtype.kVarType_SWheel or \
                id.var_type == viewtype.kVarType_DWheel or id.var_type == viewtype.kVarType_SDDExtra or id.var_type == viewtype.kVarType_OperationTarget:
            valid_item = mthead.var_report_items()
            valid_item.var_id=id.var_id
            valid_item.var_type=id.var_type
            valid_list.append(valid_item)
    return valid_list

#根据类型,返回build数据
def get_var_data(var_id,type_id,var_data):
    print('mt_build_var')
    var_dict=[]
    if type_id == viewtype.kVarType_CanBus:
        can_data = view_data.var__can_device_t()
        if can_data.length()==len(var_data):
            can_data.build(var_data, 0)
            var_dict=[{'canbus':can_data.canbus_.value,},{'canport':can_data.canport_.value},{'cannode':can_data.cannode_.value},
                      {'latency': can_data.latency_.value},{'merge':can_data.merge_.value},{'self_rw64':can_data.self_rw64_.value},
                      {'pdocnt': can_data.pdocnt_.value}]
        return {var_id:var_dict}

    elif type_id == viewtype.kVarType_Elmo:
        elmo_data = view_data.var__elmo_t()
        if elmo_data.length()==len(var_data):
            elmo_data.build(var_data, 0)
            var_dict=[{'candev_head_canbus':elmo_data.candev_head_.canbus_.value},{'candev_head_canport':elmo_data.candev_head_.canport_.value},{'candev_head_cannode':elmo_data.candev_head_.cannode_.value},
                      { 'candev_head_latency': elmo_data.candev_head_.latency_.value},{'candev_head_merge':elmo_data.candev_head_.merge_.value},{'candev_head_self_rw64':elmo_data.candev_head_.self_rw64_.value},
                      {'candev_head_pdocnt': elmo_data.candev_head_.pdocnt_.value},{'profile_speed':elmo_data.profile_speed_.value},{'profile_acc':elmo_data.profile_acc_.value},
                      {'profile_dec':elmo_data.profile_dec_.value},{'status_command':elmo_data.status_.command_.value},{'status_middle':elmo_data.status_.maiddle_.value},
                      {'status_response': elmo_data.status_.response_.value},{'control_mode':elmo_data.control_mode_.value},{'command_velocity':elmo_data.command_velocity_.value},
                      {'command_position':elmo_data.command_position_.value},{'command_current':elmo_data.command_current_.value},{'enable':elmo_data.enable_.value},
                      {'node_state':elmo_data.node_state_.value},{'error_code':elmo_data.error_code_.value},{'time_stamp':elmo_data.time_stamp_.value},
                      {'actual_velocity':elmo_data.actual_velocity_.value},{'actual_position':elmo_data.actual_position_.value},{'actual_current':elmo_data.actual_current_.value},
                      {'enabled':elmo_data.enabled_.value},{'di':elmo_data.di_.value},{'do':elmo_data.do_.value}]
        return {var_id:var_dict}

    # elif type_id == viewtype.kVarType_Copley:
    #     pass

    elif type_id == viewtype.kVarType_DIO:
        dio_data = view_data.var__dio_t()
        if dio_data.length()==len(var_data):
            dio_data.build(var_data, 0)
            print('ao--',dio_data.ao_[0].data_[0],dio_data.ao_[0].start_address_.value)
            var_dict=[{'candev_head_canbus':dio_data.candev_head_.canbus_.value},{'candev_head_canport':dio_data.candev_head_.canport_.value},{'candev_head_cannode':dio_data.candev_head_.cannode_.value},
                    {'candev_head_latency': dio_data.candev_head_.latency_.value},{'candev_head_merge':dio_data.candev_head_.merge_.value},{'candev_head_self_rw64':dio_data.candev_head_.self_rw64_.value},
                    {'candev_head_pdocnt': dio_data.candev_head_.pdocnt_.value},{'di_channel_num':dio_data.di_channel_num_.value},{'do_channel_num':dio_data.do_channel_num_.value},
                    {'status_command':dio_data.status_.command_.value},{'status_middle':dio_data.status_.maiddle_.value},{'status_response':dio_data.status_.response_.value},
                    {'do':dio_data.do_.value},{'bus_state':dio_data.bus_state_.value},{'error_code':dio_data.error_code_.value},{'time_stamp':dio_data.time_stamp_.value},{'enabled':dio_data.enabled_.value},
                    {'di':dio_data.di_.value},{'do2':dio_data.do2_.value}]
            for i in range(0,10):
                tmp_dict={}
                t='ao['+str(i)+']'+'_start_address'
                tmp_dict[t]=dio_data.ao_[i].start_address_.value
                var_dict.append({t:tmp_dict[t]})
                t='ao['+str(i)+']'+'_effective_count_of_index'
                tmp_dict[t] = dio_data.ao_[i].effective_count_of_index_.value
                var_dict.append({t: tmp_dict[t]})
                t = 'ao[' + str(i) + ']' + '_internel_type'
                tmp_dict[t] = dio_data.ao_[i].internel_type_.value
                var_dict.append({t: tmp_dict[t]})
                for j in range(10):
                    tmp = 'ao[' + str(i) + ']' + '_data_'+str(j)
                    tmp_dict[tmp]=dio_data.ao_[i].data_[j].value
                    var_dict.append({tmp: tmp_dict[tmp]})

            for i in range(0,10):
                tmp_dict = {}
                t='ai['+str(i)+']'+'_start_address'
                tmp_dict[t]=dio_data.ai_[i].start_address_.value
                var_dict.append({t: tmp_dict[t]})
                t='ai['+str(i)+']'+'effective_count_of_index'
                tmp_dict[t] = dio_data.ai_[i].effective_count_of_index_.value
                var_dict.append({t: tmp_dict[t]})
                t = 'ai[' + str(i) + ']' + 'internel_type'
                tmp_dict[t] = dio_data.ai_[i].internel_type_.value
                var_dict.append({t: tmp_dict[t]})
                for j in range(10):
                    tmp = 'ai[' + str(i) + ']' + '_data_'+str(j)
                    tmp_dict[tmp]=dio_data.ai_[i].data_[j].value
                    var_dict.append({tmp:tmp_dict[tmp]})

            for i in range(10):
                t='ao2['+str(i)+']'+'_start_address'
                tmp_dict[t]=dio_data.ao2_[i].start_address_.value
                var_dict.append({t: tmp_dict[t]})
                t='ao2['+str(i)+']'+'effective_count_of_index'
                tmp_dict[t] = dio_data.ao2_[i].effective_count_of_index_.value
                var_dict.append({t: tmp_dict[t]})
                t = 'ao2[' + str(i) + ']' + 'internel_type'
                tmp_dict[t] = dio_data.ao2_[i].internel_type_.value
                var_dict.append({t: tmp_dict[t]})
                for j in range(10):
                    tmp = 'ao2[' + str(i) + ']' + '_data_'+str(j)
                    tmp_dict[tmp]=dio_data.ao2_[i].data_[j].value
                    var_dict.append({tmp: tmp_dict[tmp]})
        return {var_id:var_dict}

    elif type_id == viewtype.kVarType_Moons:
        moons_data = view_data.var__moons_t()
        if moons_data.length()==len(var_data):
            moons_data.build(var_data, 0)
            var_dict=[{'candev_head_canbus':moons_data.candev_head_.canbus_.value},{'candev_head_canport':moons_data.candev_head_.canport_.value},{'candev_head_cannode':moons_data.candev_head_.cannode_.value},
                    {'candev_head_latency': moons_data.candev_head_.latency_.value},{'candev_head_merge':moons_data.candev_head_.merge_.value},{'candev_head_self_rw64':moons_data.candev_head_.self_rw64_.value},
                    {'candev_head_pdocnt': moons_data.candev_head_.pdocnt_.value},{'profile_speed':moons_data.profile_speed_.value},{'profile_acc':moons_data.profile_acc_.value},
                    {'profile_dec_':moons_data.profile_dec_.value},{'status_command':moons_data.status_.command_.value},{'status_middle':moons_data.status_.maiddle_.value},
                    {'status_response': moons_data.status_.response_.value},{'control_mode':moons_data.control_mode_.value},{'command_velocity':moons_data.command_velocity_.value},
                    {'command_position':moons_data.command_position_.value},{'command_current':moons_data.command_current_.value},{'enable':moons_data.enable_.value},
                    {'state_command':moons_data.status_.command_.value},{'state_maiddle':moons_data.status_.maiddle_.value},{'state_response':moons_data.status_.response_.value},
                    {'error_code':moons_data.error_code_.value},{'time_stamp':moons_data.time_stamp_.value},
                    {'actual_velocity_':moons_data.actual_velocity_.value},{'actual_position_':moons_data.actual_position_.value},{'actual_current':moons_data.actual_current_.value},
                    {'enabled':moons_data.enabled_.value},{'di':moons_data.di_.value},{'do':moons_data.do_.value}]
        return {var_id:var_dict}

    elif type_id == viewtype.kVarType_AngleEncoder:
        angle_data = view_data.var__angle_encoder_t()
        if angle_data.length()==len(var_data):
            angle_data.build(var_data, 0)
            var_dict=[{'candev_head_canbus':angle_data.candev_head_.canbus_.value},{'candev_head_canport':angle_data.candev_head_.canport_.value},{'candev_head_cannode':angle_data.candev_head_.cannode_.value},
                    { 'candev_head_latency': angle_data.candev_head_.latency_.value},{'candev_head_merge':angle_data.candev_head_.merge_.value},{'candev_head_self_rw64':angle_data.candev_head_.self_rw64_.value},
                    { 'candev_head_pdocnt': angle_data.candev_head_.pdocnt_.value},{'angle_encoder_type':angle_data.angle_encoder_type_t.value},{'state':angle_data.state_.value},
                    { 'actual_angle':angle_data.actual_angle_.value},{'error_code':angle_data.error_code_.value},{'time_stamp':angle_data.time_stamp_.value}]
        return {var_id:var_dict}

    elif type_id == viewtype.kVarType_SafetyProtec:
        safe_data=view_data.var__safety_t()
        if safe_data.length()==len(var_data):
            safe_data.build(var_data,0)

            var_dict=[{'enable':safe_data.enable_.value},{'enabled':safe_data.enabled_.value},{'cur_bank_id':safe_data.cur_bank_id_.value},{'cur_bank_level':safe_data.cur_bank_level.value},
                    {'safety_reslut':safe_data.safety_reslut_.value},{'sensor_trrigered_src_dev_id':safe_data.sensor_trrigered_.src_dev_id.value},
                    {'sensor_trrigered_src_dev_type':safe_data.sensor_trrigered_.src_dev_type.value},
                    {'sensor_trrigered_data_src_channel[0]': safe_data.sensor_trrigered_.data_src_channel[0].value},
                    {'sensor_trrigered_data_src_channel[1]': safe_data.sensor_trrigered_.data_src_channel[1].value},
                    {'sensor_trrigered_data_src_channel[2]': safe_data.sensor_trrigered_.data_src_channel[2].value},
                    {'sensor_trrigered_dev_data_type':safe_data.sensor_trrigered_.dev_data_type.value},
                    {'sensor_trrigered_reslut': safe_data.sensor_trrigered_.reslut.value},{'sensor_trrigered_sensor_name':str(safe_data.sensor_trrigered_.sensor_name)},
                    {'sensor_trrigered_ai_thres': safe_data.sensor_trrigered_.ai_thres.value},{'sensor_trrigered_ai_cur':safe_data.sensor_trrigered_.ai_cur.value},
                    {'manual_bank_id':safe_data.manual_bank_id_.value},{'manual_bank_level':safe_data.manual_bank_level_.value}]
        return {var_id:var_dict}

    elif type_id == viewtype.kVarType_Vehicle:
        vehi_data = view_data.vehicle_t()
        if vehi_data.length()==len(var_data):
            vehi_data.build(var_data, 0)
            var_dict=[{'vehicle_id':vehi_data.vehicle_id_.value},{'vehicle_name':str(vehi_data.vehicle_name_)},{'vehicle_type':vehi_data.vehicle_type_.value},
                {'chassis_type': vehi_data.chassis_type_},{'max_speed':vehi_data.max_speed_.value},{'creep_speed':vehi_data.creep_speed_.value},
                {'max_acc': vehi_data.max_acc_.value},{'max_dec':vehi_data.max_dec_.value},{'max_w':vehi_data.max_w_.value},
                {'creep_w': vehi_data.creep_w_.value},{'max_acc_w':vehi_data.max_acc_w_.value},{'max_dec_w':vehi_data.max_dec_w_.value},
                {'steer_angle_error_tolerance': vehi_data.steer_angle_error_tolerance_.value},{'manual_velocity_x':vehi_data.manual_velocity_.x_.value},{'manual_velocity_y':vehi_data.manual_velocity_.y_.value},
                {'manual_velocity_angle':vehi_data.manual_velocity_.angle_.value},
                {'stop_normal':vehi_data.stop_normal_.value},{ 'stop_emergency': vehi_data.stop_emergency_.value},{'fault_stop':vehi_data.fault_stop_.value},{'slow_down':vehi_data.slow_down_.value},
                {'enable': vehi_data.enable_.value},{'control_mode':vehi_data.control_mode_.value},{'enabled':vehi_data.enabled_.value},{'command_velocity_x':vehi_data.command_velocity_.x_.value},
                {'command_velocity_y':vehi_data.command_velocity_.y_.value},{'command_velocity_angle':vehi_data.command_velocity_.angle_.value},
                {'ref_velocity_x':vehi_data.ref_velocity_.x_.value},{ 'ref_velocity_y':vehi_data.ref_velocity_.y_.value},{ 'ref_velocity_angle':vehi_data.ref_velocity_.angle_.value},
                {'actual_command_velocity_x':vehi_data.actual_command_velocity_.x_ .value},{ 'actual_command_velocity_y':vehi_data.actual_command_velocity_.y_ .value},
                { 'actual_command_velocity_angle':vehi_data.actual_command_velocity_.angle_.value},
                {'actual_velocity_x':vehi_data.actual_velocity_.x_.value},{ 'actual_velocity_y':vehi_data.actual_velocity_.y_.value},{ 'actual_velocity_angle':vehi_data.actual_velocity_.angle_.value},
                {'odo_meter_x':vehi_data.odo_meter_.x_ .value},{ 'odo_meter_y':vehi_data.odo_meter_.y_ .value},{ 'odo_meter_angle':vehi_data.odo_meter_.angle_.value},
                {'time_stamp': vehi_data.time_stamp_.value},{ 'is_moving':vehi_data.is_moving_.value},{ 'normal_stopped':vehi_data.normal_stopped_.value},{ 'emergency_stopped':vehi_data.emergency_stopped_.value},
                {'slow_done': vehi_data.slow_done_.value},{ 'total_odo_meter':vehi_data.total_odo_meter_.value}]
        return {var_id:var_dict}

    elif type_id == viewtype.kVarType_Navigation:
        nav_view = view_data.navigation_t()
        if nav_view.length()==len(var_data):
            nav_view.build(var_data, 0)
            var_dict=[{'max_speed':nav_view.max_speed_.value},{'creep_speed':nav_view.creep_speed_.value},{'max_w':nav_view.max_w_.value},
                {'creep_w':nav_view.creep_w_.value},{'slow_down_speed_':nav_view.slow_down_speed_.value},{'acc':nav_view.acc_.value},{'dec':nav_view.dec_.value},{'dec_estop':nav_view.dec_estop_.value},{'acc_w':nav_view.acc_w_.value},
                {'dec_w':nav_view.dec_w_.value},{'creep_distance':nav_view.creep_distance_.value},{'creep_theta':nav_view.creep_theta_.value},{'upl_mapping_angle_tolerance':nav_view.upl_mapping_angle_tolerance_.value},
                {'upl_mapping_dist_tolerance':nav_view.upl_mapping_dist_tolerance_.value},{'upl_mapping_angle_weight':nav_view.upl_mapping_angle_weight_.value},{'upl_mapping_dist_weight':nav_view.upl_mapping_dist_weight_.value},
                {'tracking_error_tolerance_dist':nav_view.tracking_error_tolerance_dist_.value},{'tracking_error_tolerance_angle':nav_view.tracking_error_tolerance_angle_.value},
                {'aim_dist':nav_view.aim_dist_.value},{'predict_time':nav_view.predict_time_.value},{'is_traj_whole':nav_view.is_traj_whole_.value},{'aim_angle_p_':nav_view.aim_angle_p_.value},
                {'aim_angle_i':nav_view.aim_angle_i_.value},{'aim_angle_d':nav_view.aim_angle_d_.value},{'stop_tolerance':nav_view.stop_tolerance_.value},{'stop_tolerance_angle':nav_view.stop_tolerance_angle_.value},
                {'stop_point_trim':nav_view.stop_point_trim_.value},{'aim_ey_p':nav_view.aim_ey_p_.value},{'aim_ey_i':nav_view.aim_ey_i_.value},{'aim_ey_d':nav_view.aim_ey_d_.value},
                {'track_status_command':nav_view.track_status_.command_.value},{ 'track_status_middle': nav_view.track_status_.maiddle_.value},{'track_status_response':nav_view.track_status_.response_.value},
                {'user_task_id':nav_view.user_task_id_.value},{'ato_task_id':nav_view.ato_task_id_.value},{'dest_upl_edge_id':nav_view.dest_upl_.edge_id_.value},
                      {'dest_upl_percentage':nav_view.dest_upl_.percentage_.value},{'dest_upl_angle':nav_view.dest_upl_.angle_.value},
                {'dest_pos_x':nav_view.dest_pos_.x_.value},{ 'dest_pos_y': nav_view.dest_pos_.y_.value},{ 'dest_pos_angle': nav_view.dest_pos_.angle_.value},
                {'traj_ref_count': nav_view.traj_ref_.count_.value},{ 'traj_ref_data': nav_view.traj_ref_.data_.value},
                {'pos:x':nav_view.pos_.x_.value},{'pos:y':nav_view.pos_.y_.value},{'pos:angle':nav_view.pos_.angle_.value},{'pos_time_stamp':nav_view.pos_time_stamp_.value},{'pos_status':nav_view.pos_status_.value},
                {'pos_confidence':nav_view.pos_confidence_.value},{'traj_ref_index_curr':nav_view.traj_ref_index_curr_.value},
                {'upl_edge_id': nav_view.upl_.edge_id_.value},{'upl_percentage': nav_view.upl_.percentage_.value},{ 'upl_angle': nav_view.upl_.angle_.value},
                {'tracking_error':nav_view.tracking_error_.value},{ 'base_point_x': nav_view.base_point_.x_.value},{ 'base_point_y': nav_view.base_point_.x_.value},{ 'base_point_angle': nav_view.base_point_.angle_.value},
                {'aim_point_x': nav_view.aim_point_.x_.value},{ 'aim_point_y': nav_view.aim_point_.x_.value},{'aim_point_angle': nav_view.aim_point_.angle_.value},
                {'aim_heading_error':nav_view.aim_heading_error_.value},{'predict_point_x': nav_view.predict_point_.x_.value},{ 'predict_point_y': nav_view.predict_point_.x_.value},
                {'predict_point_angle': nav_view.predict_point_.angle_.value},{'predict_point_curvature':nav_view.predict_point_curvature_.value},
                {'on_last_segment':nav_view.on_last_segment_.value},{'dist_to_partition':nav_view.dist_to_partition_.value},{'dist_to_dest':nav_view.dist_to_dest_.value},
                {'current_task_id':nav_view.current_task_id_.value},{'runtime_limiting_velocity':nav_view.runtime_limiting_velocity_.value},
                { 'pos_x': nav_view.pos_.x_.value},{ 'pos_y': nav_view.pos_.y_.value},{ 'pos_angle': nav_view.pos_.angle_.value},
                { 'current_edge_wop_properties_wop_id': nav_view.current_edge_wop_properties_.wop_id_.value},{'current_edge_wop_properties_enabled_': nav_view.current_edge_wop_properties_.enabled_.value}]
                    #'current_edge_wop_properties_wop_properties': nav_view.current_edge_wop_properties_.wop_properties_}
        return {var_id:var_dict}

    elif type_id == viewtype.kVarType_Operation:
        oper_data = view_data.operation_t()
        if oper_data.length()==len(var_data):
            oper_data.build(var_data, 0)
            var_dict=[{'status_command':oper_data.status_.command_.value},{'status_middle':oper_data.status_.maiddle_.value},{'status_response':oper_data.status_.response_.value},
                {'user_task_id_':oper_data.user_task_id_.value},{'ato_task_id':oper_data.ato_task_id_.value},{'code':oper_data.code_.value},{'param0_':oper_data.param0_.value},{'param1':oper_data.param1_.value},
                {'param2_': oper_data.param2_.value},{'param3_':oper_data.param3_.value},{'param4_':oper_data.param4_.value},{'param5_':oper_data.param5_.value},{'param6_':oper_data.param6_.value},
                {'param7_': oper_data.param0_.value},{'param8_':oper_data.param0_.value},{'param9_':oper_data.param0_.value},{'param10_':oper_data.param0_.value},{'param11_':oper_data.param11_.value},
                {'param11': oper_data.param11_.value},{'param12':oper_data.param12_.value},{'param13':oper_data.param13_.value},{'param14':oper_data.param14_.value},{'param15':oper_data.param15_.value},
                {'param16': oper_data.param16_.value},{'param17':oper_data.param17_.value},{'param18':oper_data.param18_.value},{'param19':oper_data.param19_.value}]
        return {var_id:var_dict}

    elif type_id == viewtype.kVarType_UserDefined:
        user_data=view_data.var__usrdef_buffer_t()
        if user_data.length()==len(var_data):
            user_data.build(var_data,0)
            var_dict=[{'usrbuf':str(user_data.usrbuf_)}]
        return {var_id:var_dict}

    elif type_id == viewtype.kVarType_SWheel:
        swheel_data=view_data.var__swheel_t()
        if swheel_data.length()==len(var_data):
            swheel_data.build(var_data,0)
            var_dict=[{'min_angle':swheel_data.min_angle_.value},{'max_angle':swheel_data.max_angle_.value},{'zero_angle':swheel_data.zero_angle_.value},
                {'zero_angle_enc':swheel_data.zero_angle_enc_.value},{'max_w':swheel_data.max_w_.value},{'control_mode':swheel_data.control_mode_.value},
                {'scale_control':swheel_data.scale_control_.value},{'scale_feedback':swheel_data.scale_feedback_.value},{'control_cp':swheel_data.control_cp_.value},
                {'control_ci':swheel_data.control_ci_.value},{'control_cd':swheel_data.control_cd_.value},{'enabled':swheel_data.enabled_.value},
                {'actual_angle':swheel_data.actual_angle_.value},{'actual_angle_enc':swheel_data.actual_angle_enc_.value},{'time_stamp':swheel_data.time_stamp_.value},
                {'error_code':swheel_data.error_code_.value},{'enable':swheel_data.enable_.value},{'command_angle':swheel_data.command_angle_.value},
                {'command_angle_enc':swheel_data.command_angle_enc_.value},{'command_rate':swheel_data.command_rate_.value},{'command_rate_enc':swheel_data.command_rate_enc_.value}]
        return {var_id:var_dict}

    elif type_id == viewtype.kVarType_DWheel:
        dwheel_data=view_data.var__dwheel_t()
        if dwheel_data.length()==len(var_data):
            dwheel_data.build(var_data,0)
            var_dict=[{'max_speed':dwheel_data.max_speed_.value},{'max_acc':dwheel_data.max_acc_.value},{'max_dec':dwheel_data.max_dec_.value},{'control_mode':dwheel_data.control_mode_.value},
                {'scale_control':dwheel_data.scale_control_.value},{'scale_feedback':dwheel_data.scale_control_.value},{'roll_weight':dwheel_data.roll_weight_.value},
                {'slide_weight':dwheel_data.slide_weight_.value},{'enabled':dwheel_data.enabled_.value},{'actual_velocity':dwheel_data.actual_velocity_.value},
                {'actual_velocity_enc':dwheel_data.actual_velocity_enc_.value},{'actual_position':dwheel_data.actual_position_.value},{'actual_position_enc':dwheel_data.actual_position_enc_.value},
                {'actual_current':dwheel_data.actual_current_.value},{'time_stamp':dwheel_data.time_stamp_.value},{'error_code':dwheel_data.error_code_.value},
                {'enable':dwheel_data.enable_.value},{'command_velocity':dwheel_data.command_velocity_.value},{'command_velocity_enc':dwheel_data.command_velocity_enc_.value},
                {'command_position':dwheel_data.command_position_.value},{'command_position_enc':dwheel_data.command_position_enc_.value},{'command_current':dwheel_data.command_current_.value}]
        return {var_id:var_dict}

    elif type_id == viewtype.kVarType_SDDExtra:
        sdd_dat=view_data.var__sdd_extra()
        if sdd_dat.length()==len(var_data):
            sdd_dat.build(var_data,0)
            var_dict=[{'guage':sdd_dat.gauge_.value},{'abc':sdd_dat.gauge_.value}]
        return {var_id:var_dict}

    elif type_id == viewtype.kVarType_OperationTarget:
        oprtar_data=view_data.optpar_t()
        if oprtar_data.length()==len(var_data):
            oprtar_data.build(var_data,0)
            var_dict=[{'ull00':oprtar_data.ull00_.value},{'ull01':oprtar_data.ull01_.value},{'ull02':oprtar_data.ull02_.value},{'ull03':oprtar_data.ull03_.value},{'ull04':oprtar_data.ull04_.value},
                {'ull05': oprtar_data.ull05_.value},{'ull06':oprtar_data.ull06_.value},{'ull07':oprtar_data.ull07_.value},{'ull08':oprtar_data.ull08_.value},{'ull09':oprtar_data.ull09_.value},
                {'ull10': oprtar_data.ull10_.value},{'ull11': oprtar_data.ull11_.value},{'ull12': oprtar_data.ull12_.value},{'ull13': oprtar_data.ull13_.value},{'ull14': oprtar_data.ull14_.value},
                {'ull15': oprtar_data.ull15_.value},{'ull16': oprtar_data.ull16_.value},{'ull17': oprtar_data.ull17_.value},{'ull18': oprtar_data.ull18_.value},{'ull19': oprtar_data.ull19_.value}]
        return {var_id:var_dict}

    else:pass
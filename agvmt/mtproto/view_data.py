from pynsp.serialize import *

def build_int(data,offset,cb):
    value=list()
    for i in range(cb):
        ttt = proto_int()
        ttt.build(data[offset:offset + 4], 0)
        value.append(ttt)
        offset = offset+4
    off=offset
    return off,value

def serialize_int(value):
    return struct.pack('i', value)
    #value.serialize()


def build_char(data,offset,cb):
    value = struct.unpack('{0}s'.format(cb), data[offset:offset + cb])[0].decode('utf-8')
    if cb >1:
        re_value=value.find('\0')
        if re_value!=0:
            off = offset + cb
            return off, value[0:re_value]
    off = offset + cb
    return off,value

def serialize_char(value,cb):
    return struct.pack('{}s'.format(cb), value.encode('utf-8'))
    #value.serialize()

class var__status_describe_t(proto_interface):
    def __init__(self):
        super(var__status_describe_t, self).__init__()
        self.command_=proto_uint32()
        self.maiddle_=proto_uint32()
        self.response_=proto_uint32()

    def length(self) -> int:
        return self.command_.length() + self.maiddle_.length()+self.response_.length()

    def serialize(self)->bytes:
        return self.command_.serialize() + self.maiddle_.serialize()+self.response_.serialize()

    def build(self, data, offset)->int:
        offset= self.command_.build(data, offset)
        offset = self.maiddle_.build(data, offset)
        return self.response_.build(data, offset)

class upl_t():
    def __init__(self):
        super(upl_t, self).__init__()
        self.edge_id_=proto_int()
        self.percentage_=proto_double()
        self.angle_=proto_double()

    def length(self) -> int:
        return self.edge_id_.length() + self.percentage_.length() + self.angle_.length()

    def serialize(self) -> bytes:
        return self.edge_id_.serialize() + self.percentage_.serialize() + self.angle_.serialize()

    def build(self, data, offset) -> int:
        offset = self.edge_id_.build(data, offset)
        offset = self.percentage_.build(data, offset)
        return self.angle_.build(data, offset)

class position_t():
    def __init__(self):
        super(position_t, self).__init__()
        self.x_=proto_double()
        self.y_=proto_double()
        self.angle_=proto_double()

    def length(self) -> int:
        return self.x_.length() + self.y_.length() + self.angle_.length()

    def serialize(self) -> bytes:
        return self.x_.serialize() + self.y_.serialize() + self.angle_.serialize()

    def build(self, data, offset) -> int:
        offset = self.x_.build(data, offset)
        offset = self.y_.build(data, offset)
        return self.angle_.build(data, offset)


class var__vector_t():
    def __init__(self):
        super(var__vector_t, self).__init__()
        self.count_=proto_int()
        self.data_=proto_uint64()

    def length(self) -> int:
        return self.count_.length() + self.data_.length()

    def serialize(self) -> bytes:
        return self.count_.serialize() + self.data_.serialize()

    def build(self, data, offset) -> int:
        offset = self.count_.build(data, offset)
        return self.data_.build(data, offset)


class var__edge_wop_properties_t():
    def __init__(self):
        super(var__edge_wop_properties_t, self).__init__()
        self.wop_id_=proto_int()
        self.enabled_=proto_int()
        self.wop_properties_=list()

    def length(self) -> int:
        return self.wop_id_.length() + self.enabled_.length() + self.enabled_.length()*9

    def serialize(self) -> bytes:
        return self.wop_id_.serialize() + self.enabled_.serialize() + serialize_int(self.wop_properties_[0])+ serialize_int(self.wop_properties_[1])+ serialize_int(self.wop_properties_[2])\
               + serialize_int(self.wop_properties_[3])+ serialize_int(self.wop_properties_[4])+ serialize_int(self.wop_properties_[5])+ serialize_int(self.wop_properties_[6]) \
               + serialize_int(self.wop_properties_[7])+ serialize_int(self.wop_properties_[8])

    def build(self, data, offset) -> int:
        offset = self.wop_id_.build(data, offset)
        offset = self.enabled_.build(data, offset)
        (offset, self.wop_properties_) = build_int(data, offset, 9)
        return offset

class var_velocity_t():
    def __init__(self):
        super(var_velocity_t, self).__init__()
        self.x_=proto_double()
        self.y_=proto_double()
        self.angle_=proto_double()

    def length(self) -> int:
        return self.x_.length() + self.y_.length() + self.angle_.length()

    def serialize(self) -> bytes:
        return self.x_.serialize() + self.y_.serialize() + self.angle_.serialize()

    def build(self, data, offset) -> int:
        offset = self.x_.build(data, offset)
        offset = self.y_.build(data, offset)
        return self.angle_.build(data, offset)

class var__dio_canbus_usrdef_block_t():
    def __init__(self):
        super(var__dio_canbus_usrdef_block_t, self).__init__()
        self.start_address_=proto_int()
        self.effective_count_of_index_=proto_int()
        self.internel_type_=proto_int()
        self.data_=list()

    def length(self)->int:
        return self.start_address_.length()+self.effective_count_of_index_.length()+self.internel_type_.length()+4*16

    def serialize(self)->bytes:
        return self.start_address_.serialize()+self.effective_count_of_index_.serialize()+self.internel_type_.serialize() +\
                serialize_int(self.data_[0]) + serialize_int(self.data_[1]) + serialize_int(self.data_[2]) + serialize_int(self.data_[3]) \
                + serialize_int(self.data_[4]) + serialize_int(self.data_[5]) + serialize_int(self.data_[6]) + serialize_int(self.data_[7])\
                + serialize_int(self.data_[8])+ serialize_int(self.data_[9])+ serialize_int(self.data_[10])+serialize_int(self.data_[11]) \
                + serialize_int(self.data_[12])+ serialize_int(self.data_[13]) + serialize_int(self.data_[14]) + serialize_int(self.data_[15])

    def build(self, data, offset) -> int:
        offset = self.start_address_.build(data, offset)
        offset = self.effective_count_of_index_.build(data, offset)
        offset = self.internel_type_.build(data, offset)
        (offset,self.data_)=build_int(data, offset,16)
        return offset

def build_userdef_block(data,offset,cb):
    value = list()
    for i in range(cb):
        tmp = var__dio_canbus_usrdef_block_t()
        tmp.build(data[offset:offset + tmp.length()], 0)
        value.append(tmp)
        offset = offset + tmp.length()
    off = offset
    return off, value

def serialize_userdef_block(value,cb):
    byte=b''
    for i in range(cb):
        byte+=value[i].serialize()
    return byte

def length_userdef_block(cb):
    tmp = var__dio_canbus_usrdef_block_t()
    return cb*tmp.length()

class var__can_device_t():
    def __init__(self):
        super(var__can_device_t, self).__init__()
        self.canbus_=proto_int()
        self.canport_=proto_int()
        self.cannode_=proto_int()
        self.latency_=proto_uint64()
        self.merge_=proto_int()
        self.self_rw64_=proto_uint64()
        self.pdocnt_=proto_int()

    def length(self) -> int:
        return self.canbus_.length() + self.canport_.length() + self.cannode_.length()+ self.latency_.length()\
               + self.merge_.length()+ self.self_rw64_.length()+ self.pdocnt_.length()

    def serialize(self) -> bytes:
        return self.canbus_.serialize() + self.canport_.serialize() + self.cannode_.serialize()+self.latency_.serialize()\
               + self.merge_.serialize() + self.self_rw64_.serialize()+ self.pdocnt_.serialize()

    def build(self, data, offset) -> int:
        offset = self.canbus_.build(data, offset)
        offset = self.canport_.build(data, offset)
        offset = self.cannode_.build(data, offset)
        offset = self.latency_.build(data, offset)
        offset = self.merge_.build(data, offset)
        offset = self.self_rw64_.build(data, offset)
        return self.pdocnt_.build(data, offset)

class navigation_t(proto_interface):
    def __init__(self):
        super(navigation_t, self).__init__()
        self.max_speed_=proto_double()
        self.creep_speed_=proto_double()
        self.max_w_=proto_double()
        self.creep_w_=proto_double()
        self.slow_down_speed_=proto_double()
        self.acc_=proto_double()
        self.dec_=proto_double()
        self.dec_estop_=proto_double()
        self.acc_w_=proto_double()
        self.dec_w_=proto_double()
        self.creep_distance_=proto_double()
        self.creep_theta_=proto_double()
        self.upl_mapping_angle_tolerance_=proto_double()
        self.upl_mapping_dist_tolerance_=proto_double()
        self.upl_mapping_angle_weight_=proto_double()
        self.upl_mapping_dist_weight_=proto_double()
        self.tracking_error_tolerance_dist_=proto_double()
        self.tracking_error_tolerance_angle_=proto_double()
        self.aim_dist_=proto_double()
        self.predict_time_=proto_float()
        self.is_traj_whole_=proto_uint32()
        self.aim_angle_p_=proto_double()
        self.aim_angle_i_=proto_double()
        self.aim_angle_d_=proto_double()
        self.stop_tolerance_=proto_double()
        self.stop_tolerance_angle_=proto_double()
        self.stop_point_trim_=proto_double()
        self.aim_ey_p_=proto_double()
        self.aim_ey_i_=proto_double()
        self.aim_ey_d_=proto_double()
        self.track_status_=var__status_describe_t()
        self.user_task_id_=proto_uint64()
        self.ato_task_id_=proto_uint64()
        self.dest_upl_=upl_t()
        self.dest_pos_=position_t()
        self.traj_ref_=var__vector_t()
        self.pos_=position_t()
        self.pos_time_stamp_=proto_uint64()
        self.pos_status_=proto_uint32()
        self.pos_confidence_=proto_double()
        self.traj_ref_index_curr_=proto_int()
        self.upl_=upl_t()
        self.tracking_error_=proto_int()
        self.base_point_=position_t()
        self.aim_point_=position_t()
        self.aim_heading_error_=proto_double()
        self.predict_point_=position_t()
        self.predict_point_curvature_=proto_double()
        self.on_last_segment_=proto_int()
        self.dist_to_partition_=proto_double()
        self.dist_to_dest_=proto_double()
        self.current_edge_wop_properties_=var__edge_wop_properties_t()
        self.current_task_id_=proto_uint64()
        self.runtime_limiting_velocity_=proto_double()

    def length(self) -> int:
        return self.max_speed_.length() + self.creep_speed_.length() + self.max_w_.length()+ self.creep_w_.length()+ self.slow_down_speed_.length()+ \
               self.acc_.length()+ self.dec_.length()+ self.dec_estop_.length()+ self.acc_w_.length()+self.dec_w_.length()+ self.creep_distance_.length()+ self.creep_theta_.length()+ \
               self.upl_mapping_angle_tolerance_.length()+ self.upl_mapping_dist_tolerance_.length()+ self.upl_mapping_angle_weight_.length()+ \
               self.upl_mapping_dist_weight_.length()+self.tracking_error_tolerance_dist_.length()+ self.tracking_error_tolerance_angle_.length() \
               + self.aim_dist_.length()+ self.predict_time_.length()+ self.is_traj_whole_.length()+ self.aim_angle_p_.length()+ self.aim_angle_i_.length()+ self.aim_angle_d_.length()\
               + self.stop_tolerance_.length()+ self.stop_tolerance_angle_.length()+ self.stop_point_trim_.length()+ self.aim_ey_p_.length()+ self.aim_ey_i_.length()+ self.aim_ey_d_.length()\
               + self.track_status_.length()+ self.user_task_id_.length()+ self.ato_task_id_.length()+ self.dest_upl_.length()+ self.dest_pos_.length()\
               + self.traj_ref_.length()+ self.pos_.length()+ self.pos_time_stamp_.length()+ self.pos_status_.length()+ self.pos_confidence_.length()+ self.traj_ref_index_curr_.length()\
               + self.upl_.length()+ self.tracking_error_.length()+ self.base_point_.length()+ self.aim_point_.length()+ self.aim_heading_error_.length()+ self.predict_point_.length()\
               + self.predict_point_curvature_.length()+ self.on_last_segment_.length()+ self.dist_to_partition_.length()+ self.dist_to_dest_.length()\
               + self.current_edge_wop_properties_.length()+ self.current_task_id_.length()+ self.runtime_limiting_velocity_.length()

    def serialize(self) -> bytes:
        return self.max_speed_.serialize() + self.creep_speed_.serialize() + self.max_w_.serialize()+ self.creep_w_.serialize()+ self.slow_down_speed_.serialize()+ \
               self.acc_.serialize()+ self.dec_.serialize()+ self.dec_estop_.serialize()+ self.acc_w_.serialize()+self.dec_w_.serialize()+ self.creep_distance_.serialize()+ self.creep_theta_.serialize()+ \
               self.upl_mapping_angle_tolerance_.serialize()+ self.upl_mapping_dist_tolerance_.serialize()+ self.upl_mapping_angle_weight_.serialize()+ \
               self.upl_mapping_dist_weight_.serialize()+ self.tracking_error_tolerance_dist_.serialize()+ self.tracking_error_tolerance_angle_.serialize()+ \
               self.aim_dist_.serialize()+ self.predict_time_.serialize()+ self.is_traj_whole_.serialize()+ self.aim_angle_p_.serialize()+ self.aim_angle_i_.serialize()+ self.aim_angle_d_.serialize()+ \
               self.stop_tolerance_.serialize()+ self.stop_tolerance_angle_.serialize()+ self.stop_point_trim_.serialize()+ self.aim_ey_p_.serialize()+ self.aim_ey_i_.serialize()+ self.aim_ey_d_.serialize()+ \
               self.track_status_.serialize()+ self.user_task_id_.serialize()+ self.ato_task_id_.serialize()+ self.dest_upl_.serialize()+ self.dest_pos_.serialize()\
               + self.traj_ref_.serialize()+ self.pos_.serialize()+ self.pos_time_stamp_.serialize()+ self.pos_status_.serialize()+ self.pos_confidence_.serialize()+ self.traj_ref_index_curr_.serialize()\
               + self.upl_.serialize()+ self.tracking_error_.serialize()+ self.base_point_.serialize()+ self.aim_point_.serialize()+ self.aim_heading_error_.serialize()+ self.predict_point_.serialize() \
               + self.predict_point_curvature_.serialize() + self.on_last_segment_.serialize() + self.dist_to_partition_.serialize() + self.dist_to_dest_.serialize() \
               + self.current_edge_wop_properties_.serialize() + self.current_task_id_.serialize() + self.runtime_limiting_velocity_.serialize()

    def build(self, data, offset) -> int:
        offset = self.max_speed_.build(data, offset)
        offset = self.creep_speed_.build(data, offset)
        offset = self.max_w_.build(data, offset)
        offset = self.creep_w_.build(data, offset)
        offset = self.slow_down_speed_.build(data, offset)
        offset = self.acc_.build(data, offset)
        offset = self.dec_.build(data, offset)
        offset = self.dec_estop_.build(data, offset)
        offset = self.acc_w_.build(data, offset)
        offset = self.dec_w_.build(data, offset)
        offset = self.creep_distance_.build(data, offset)
        offset = self.creep_theta_.build(data, offset)
        offset = self.upl_mapping_angle_tolerance_.build(data, offset)
        offset = self.upl_mapping_dist_tolerance_.build(data, offset)
        offset = self.upl_mapping_angle_weight_.build(data, offset)
        offset = self.upl_mapping_dist_weight_.build(data, offset)
        offset = self.tracking_error_tolerance_dist_.build(data, offset)
        offset = self.tracking_error_tolerance_angle_.build(data, offset)
        offset = self.aim_dist_.build(data, offset)
        offset = self.predict_time_.build(data, offset)
        offset = self.is_traj_whole_.build(data, offset)
        offset = self.aim_angle_p_.build(data, offset)
        offset = self.aim_angle_i_.build(data, offset)
        offset = self.aim_angle_d_.build(data, offset)
        offset = self.stop_tolerance_.build(data, offset)
        offset = self.stop_tolerance_angle_.build(data, offset)
        offset = self.stop_point_trim_.build(data, offset)
        offset = self.aim_ey_p_.build(data, offset)
        offset = self.aim_ey_i_.build(data, offset)
        offset = self.aim_ey_d_.build(data, offset)
        offset = self.track_status_.build(data, offset)
        offset = self.user_task_id_.build(data, offset)
        offset = self.ato_task_id_.build(data, offset)
        offset = self.dest_upl_.build(data, offset)
        offset = self.dest_pos_.build(data, offset)
        offset = self.traj_ref_.build(data, offset)
        offset = self.pos_.build(data, offset)
        offset = self.pos_time_stamp_.build(data, offset)
        offset = self.pos_status_.build(data, offset)
        offset = self.pos_confidence_.build(data, offset)
        offset = self.traj_ref_index_curr_.build(data, offset)
        offset = self.upl_.build(data, offset)
        offset = self.tracking_error_.build(data, offset)
        offset = self.base_point_.build(data, offset)
        offset = self.aim_point_.build(data, offset)
        offset = self.aim_heading_error_.build(data, offset)
        offset = self.predict_point_.build(data, offset)
        offset = self.predict_point_curvature_.build(data, offset)
        offset = self.on_last_segment_.build(data, offset)
        offset = self.dist_to_partition_.build(data, offset)
        offset = self.dist_to_dest_.build(data, offset)
        offset = self.current_edge_wop_properties_.build(data, offset)
        offset = self.current_task_id_.build(data, offset)
        return self.runtime_limiting_velocity_.build(data, offset)

class vehicle_t():
    def __init__(self):
        self.vehicle_id_=proto_int()
        self.vehicle_name_=''
        self.vehicle_type_=proto_int()
        self.chassis_type_=''
        self.max_speed_=proto_double()
        self.creep_speed_=proto_double()
        self.max_acc_=proto_double()
        self.max_dec_=proto_double()
        self.max_w_=proto_double()
        self.creep_w_=proto_double()
        self.max_acc_w_=proto_double()
        self.max_dec_w_=proto_double()
        self.steer_angle_error_tolerance_=proto_double()
        self.manual_velocity_=var_velocity_t()
        self.stop_normal_=proto_int()
        self.stop_emergency_=proto_int()
        self.fault_stop_=proto_int()
        self.slow_down_=proto_int()
        self.enable_=proto_int()
        self.control_mode_=proto_uint32()

        self.enabled_=proto_int()
        self.command_velocity_=var_velocity_t()
        self.ref_velocity_=var_velocity_t()
        self.actual_command_velocity_=var_velocity_t()
        self.actual_velocity_=var_velocity_t()
        self.odo_meter_=position_t()
        self.time_stamp_=proto_uint64()
        self.is_moving_=proto_int()
        self.normal_stopped_=proto_int()
        self.emergency_stopped_=proto_int()
        self.slow_done_=proto_int()

        self.total_odo_meter_=proto_double()

    def length(self) -> int:
        return self.vehicle_id_.length() + 64 + self.vehicle_type_.length()+ 1+ self.max_speed_.length()+ \
               self.creep_speed_.length()+ self.max_acc_.length()+ self.max_dec_.length()+ self.max_w_.length()+ self.creep_w_.length()+ self.max_acc_w_.length()+ \
               self.max_dec_w_.length()+ self.steer_angle_error_tolerance_.length()+ self.manual_velocity_.length()+ \
               self.stop_normal_.length()+self.stop_emergency_.length()+ self.fault_stop_.length() \
               + self.slow_down_.length()+ self.enable_.length()+ self.control_mode_.length()+self.enabled_.length()+ self.command_velocity_.length()+ self.ref_velocity_.length()+ self.actual_command_velocity_.length()\
               + self.actual_velocity_.length()+ self.odo_meter_.length()+ self.time_stamp_.length()+ self.is_moving_.length()+ self.normal_stopped_.length()+ self.emergency_stopped_.length()\
               + self.slow_done_.length()+ self.total_odo_meter_.length()

    def serialize(self) -> bytes:
        return self.vehicle_id_.serialize() + serialize_char(self.vehicle_name_,64) + self.vehicle_type_.serialize()+ serialize_char(self.chassis_type_,1)+ self.max_speed_.serialize()+ \
               self.creep_speed_.serialize()+ self.max_acc_.serialize()+ self.max_dec_.serialize()+ self.max_w_.serialize()+ self.creep_w_.serialize()+ self.max_acc_w_.serialize()+ \
               self.max_dec_w_.serialize()+ self.steer_angle_error_tolerance_.serialize()+ self.manual_velocity_.serialize()+ \
               self.stop_normal_.serialize()+ self.stop_emergency_.serialize()+ self.fault_stop_.serialize()+ \
               self.slow_down_.serialize()+ self.enable_.serialize()+ self.control_mode_.serialize()+ self.enabled_.serialize()+self.command_velocity_.serialize()+ self.ref_velocity_.serialize()+ self.actual_command_velocity_.serialize()+ \
               self.actual_velocity_.serialize()+ self.odo_meter_.serialize()+ self.time_stamp_.serialize()+ self.is_moving_.serialize()+ self.normal_stopped_.serialize()+ self.emergency_stopped_.serialize()+ \
               self.slow_done_.serialize()+ self.total_odo_meter_.serialize()

    def build(self, data, offset) -> int:
        offset = self.vehicle_id_.build(data, offset)
        (offset, self.vehicle_name_) = build_char(data,offset, 64)
        offset = self.vehicle_type_.build(data, offset)
        (offset, w) = build_char(data,offset, 1)
        self.chassis_type_ = ord(w)
        offset = self.max_speed_.build(data, offset)
        offset = self.creep_speed_.build(data, offset)
        offset = self.max_acc_.build(data, offset)
        offset = self.max_dec_.build(data, offset)
        offset = self.max_w_.build(data, offset)
        offset = self.creep_w_.build(data, offset)
        offset = self.max_acc_w_.build(data, offset)
        offset = self.max_dec_w_.build(data, offset)
        offset = self.steer_angle_error_tolerance_.build(data, offset)
        offset = self.manual_velocity_.build(data, offset)
        offset = self.stop_normal_.build(data, offset)
        offset = self.stop_emergency_.build(data, offset)
        offset = self.fault_stop_.build(data, offset)
        offset = self.slow_down_.build(data, offset)
        offset = self.enable_.build(data, offset)
        offset = self.control_mode_.build(data, offset)
        offset = self.enabled_.build(data, offset)
        offset = self.command_velocity_.build(data, offset)
        offset = self.ref_velocity_.build(data, offset)
        offset = self.actual_command_velocity_.build(data, offset)
        offset = self.actual_velocity_.build(data, offset)
        offset = self.odo_meter_.build(data, offset)
        offset = self.time_stamp_.build(data, offset)
        offset = self.is_moving_.build(data, offset)
        offset = self.normal_stopped_.build(data, offset)
        offset = self.emergency_stopped_.build(data, offset)
        offset = self.slow_done_.build(data, offset)
        return self.total_odo_meter_.build(data, offset)

class operation_t():
    def __init__(self):
        super(operation_t, self).__init__()
        self.status_=var__status_describe_t()
        self.user_task_id_=proto_uint64()
        self.ato_task_id_=proto_uint64()
        self.code_=proto_int()
        self.param0_=proto_uint64()
        self.param1_=proto_uint64()
        self.param2_ = proto_uint64()
        self.param3_ = proto_uint64()
        self.param4_ = proto_uint64()
        self.param5_ = proto_uint64()
        self.param6_ = proto_uint64()
        self.param7_ = proto_uint64()
        self.param8_ = proto_uint64()
        self.param9_ = proto_uint64()

        self.param10_ = proto_uint64()
        self.param11_ = proto_uint64()
        self.param12_ = proto_uint64()
        self.param13_ = proto_uint64()
        self.param14_ = proto_uint64()
        self.param15_ = proto_uint64()
        self.param16_ = proto_uint64()
        self.param17_ = proto_uint64()
        self.param18_ = proto_uint64()
        self.param19_ = proto_uint64()

        self.current_task_id=proto_uint64()

    def length(self) -> int:
        return self.status_.length() + self.user_task_id_.length()+ self.ato_task_id_.length()+ self.code_.length()+ self.param0_.length()+ self.param1_.length()+\
               self.param2_.length()+ self.param3_.length()+ self.param4_.length()+ self.param5_.length()+ self.param6_.length()+ self.param7_.length()+ \
               self.param8_.length()+ self.param9_.length()+ self.param10_.length()+ self.param11_.length()+ self.param12_.length()+ self.param13_.length()+\
               self.param14_.length()+ self.param15_.length()+ self.param16_.length()+ self.param17_.length()+ self.param18_.length()+ self.param19_.length()+self.current_task_id.length()

    def serialize(self) -> bytes:
        return self.status_.serialize() + self.user_task_id_.serialize()+ self.ato_task_id_.serialize()+ self.code_.serialize()+ self.param0_.serialize()+ self.param1_.serialize()+ \
               self.param4_.serialize() + self.param3_.serialize()+ self.param4_.serialize()+ self.param5_.serialize()+ self.param6_.serialize()+ self.param7_.serialize()+ \
               self.param8_.serialize() + self.param9_.serialize() + self.param10_.serialize() + self.param11_.serialize() + self.param12_.serialize()+ self.param13_.serialize() + \
               self.param14_.serialize() + self.param15_.serialize() + self.param16_.serialize() + self.param17_.serialize() + self.param18_.serialize()+ self.param19_.serialize()+self.current_task_id.serialize()

    def build(self, data, offset) -> int:
        offset = self.status_.build(data, offset)
        offset = self.user_task_id_.build(data, offset)
        offset = self.ato_task_id_.build(data, offset)
        offset = self.code_.build(data, offset)
        offset = self.param0_.build(data, offset)
        offset = self.param1_.build(data, offset)
        offset = self.param2_.build(data, offset)
        offset = self.param3_.build(data, offset)
        offset = self.param4_.build(data, offset)
        offset = self.param5_.build(data, offset)
        offset = self.param6_.build(data, offset)
        offset = self.param7_.build(data, offset)
        offset = self.param8_.build(data, offset)
        offset = self.param9_.build(data, offset)
        offset = self.param10_.build(data, offset)
        offset = self.param11_.build(data, offset)
        offset = self.param12_.build(data, offset)
        offset = self.param13_.build(data, offset)
        offset = self.param14_.build(data, offset)
        offset = self.param15_.build(data, offset)
        offset = self.param16_.build(data, offset)
        offset = self.param17_.build(data, offset)
        offset = self.param18_.build(data, offset)
        offset = self.param19_.build(data, offset)
        return self.current_task_id.build(data,offset)

class optpar_t():
    def __init__(self):
        super(optpar_t, self).__init__()
        self.ull00_=proto_uint64()
        self.ull01_=proto_uint64()
        self.ull02_ = proto_uint64()
        self.ull03_ = proto_uint64()
        self.ull04_ = proto_uint64()
        self.ull05_ = proto_uint64()
        self.ull06_ = proto_uint64()
        self.ull07_ = proto_uint64()
        self.ull08_ = proto_uint64()
        self.ull09_ = proto_uint64()
        self.ull10_ = proto_uint64()
        self.ull11_ = proto_uint64()
        self.ull12_ = proto_uint64()
        self.ull13_ = proto_uint64()
        self.ull14_ = proto_uint64()
        self.ull15_ = proto_uint64()
        self.ull16_ = proto_uint64()
        self.ull17_ = proto_uint64()
        self.ull18_ = proto_uint64()
        self.ull19_ = proto_uint64()

    def length(self) -> int:
        return self.ull00_.length()+ self.ull01_.length()+self.ull02_.length()+ self.ull03_.length()+ self.ull04_.length()+ self.ull05_.length()+ self.ull06_.length()+\
               self.ull07_.length()+ self.ull08_.length()+ self.ull09_.length()+ self.ull10_.length()+ self.ull11_.length()+ self.ull12_.length()+ self.ull13_.length()+\
               self.ull14_.length()+ self.ull15_.length()+ self.ull16_.length()+ self.ull17_.length()+ self.ull18_.length()+ self.ull19_.length()

    def serialize(self) -> bytes:
        return self.ull00_.serialize() + self.ull01_.serialize()+ self.ull02_.serialize()+ self.ull03_.serialize()+ self.ull04_.serialize()+ self.ull05_.serialize()+ \
               self.ull06_.serialize() + self.ull07_.serialize()+ self.ull08_.serialize()+ self.ull09_.serialize()+ self.ull10_.serialize()+ self.ull11_.serialize()+ \
               self.ull12_.serialize() + self.ull13_.serialize() + self.ull14_.serialize() + self.ull15_.serialize() + self.ull16_.serialize()+ self.ull17_.serialize() + \
               self.ull18_.serialize() + self.ull19_.serialize()

    def build(self, data, offset) -> int:
        offset = self.ull00_.build(data, offset)
        offset = self.ull01_.build(data, offset)
        offset = self.ull02_.build(data, offset)
        offset = self.ull03_.build(data, offset)
        offset = self.ull04_.build(data, offset)
        offset = self.ull05_.build(data, offset)
        offset = self.ull06_.build(data, offset)
        offset = self.ull07_.build(data, offset)
        offset = self.ull08_.build(data, offset)
        offset = self.ull09_.build(data, offset)
        offset = self.ull10_.build(data, offset)
        offset = self.ull11_.build(data, offset)
        offset = self.ull12_.build(data, offset)
        offset = self.ull13_.build(data, offset)
        offset = self.ull14_.build(data, offset)
        offset = self.ull15_.build(data, offset)
        offset = self.ull16_.build(data, offset)
        offset = self.ull17_.build(data, offset)
        offset = self.ull18_.build(data, offset)
        return self.ull19_.build(data, offset)

class var__elmo_t():
    def __init__(self):
        super(var__elmo_t, self).__init__()
        self.candev_head_=var__can_device_t()
        self.profile_speed_=proto_double()
        self.profile_acc_=proto_double()
        self.profile_dec_=proto_double()
        self.status_ = var__status_describe_t()
        self.control_mode_=proto_uint32()
        self.command_velocity_=proto_int64()
        self.command_position_=proto_int64()
        self.command_current_=proto_double()
        self.enable_=proto_int()
        self.node_state_=proto_int()
        self.error_code_=proto_int()
        self.time_stamp_=proto_uint64()
        self.actual_velocity_=proto_int64()
        self.actual_position_=proto_int64()
        self.actual_current_=proto_double()
        self.enabled_=proto_int()
        self.di_=proto_int()
        self.do_=proto_int()

    def length(self) -> int:
        return self.candev_head_.length() + self.profile_speed_.length()+ self.profile_acc_.length()+ self.profile_dec_.length()+ \
               self.status_.length()+ self.control_mode_.length()+ self.command_velocity_.length()+ self.command_position_.length()+ \
               self.command_current_.length()+ self.enable_.length()+ self.node_state_.length()+ self.error_code_.length()+ \
               self.time_stamp_.length()+ self.actual_velocity_.length()+ self.actual_position_.length()+ self.actual_current_.length()+ \
               self.enabled_.length()+self.di_.length()+self.do_.length()

    def serialize(self) -> bytes:
        return self.candev_head_.serialize() + self.profile_speed_.serialize()+ self.profile_acc_.serialize()+ \
               self.profile_dec_.serialize()+ self.status_.serialize()+ self.control_mode_.serialize()+ \
               self.command_velocity_.serialize()+ self.command_position_.serialize()+ self.command_current_.serialize()+ \
               self.enable_.serialize() + self.node_state_.serialize() + self.error_code_.serialize() + \
               self.time_stamp_.serialize()+ self.actual_velocity_.serialize()+ self.actual_position_.serialize()+ self.actual_current_.serialize()\
               +self.enabled_.serialize()+self.di_.serialize()+self.do_.serialize()

    def build(self, data, offset) -> int:
        offset = self.candev_head_.build(data, offset)
        offset = self.profile_speed_.build(data, offset)
        offset = self.profile_acc_.build(data, offset)
        offset = self.profile_dec_.build(data, offset)
        offset = self.status_.build(data, offset)
        offset = self.control_mode_.build(data, offset)
        offset = self.command_velocity_.build(data, offset)
        offset = self.command_position_.build(data, offset)
        offset = self.command_current_.build(data, offset)
        offset = self.enable_.build(data, offset)
        offset = self.node_state_.build(data, offset)
        offset = self.error_code_.build(data, offset)
        offset = self.time_stamp_.build(data, offset)
        offset = self.actual_velocity_.build(data, offset)
        offset = self.actual_position_.build(data, offset)
        offset = self.actual_current_.build(data, offset)
        offset = self.enabled_.build(data, offset)
        offset = self.di_.build(data, offset)
        offset = self.do_.build(data, offset)
        return offset

class var__moons_t():
    def __init__(self):
        super(var__moons_t, self).__init__()
        self.candev_head_=var__can_device_t()
        self.profile_speed_=proto_double()
        self.profile_acc_=proto_double()
        self.profile_dec_=proto_double()
        self.status_ = var__status_describe_t()
        self.control_mode_=proto_uint32()
        self.command_velocity_=proto_int64()
        self.command_position_=proto_int64()
        self.command_current_=proto_double()
        self.enable_=proto_int()
        self.state_=proto_int()
        self.error_code_=proto_int()
        self.time_stamp_=proto_uint64()
        self.actual_velocity_=proto_int64()
        self.actual_position_=proto_int64()
        self.actual_current_=proto_double()
        self.enabled_=proto_int()
        self.di_=proto_int()
        self.do_=proto_int()

    def length(self) -> int:
        return self.candev_head_.length() + self.profile_speed_.length()+ self.profile_acc_.length()+ self.profile_dec_.length()+ \
               self.status_.length()+ self.control_mode_.length()+ self.command_velocity_.length()+ self.command_position_.length()+ \
               self.command_current_.length()+ self.enable_.length()+ self.state_.length()+ self.error_code_.length()+ \
               self.time_stamp_.length()+ self.actual_velocity_.length()+ self.actual_position_.length()+ self.actual_current_.length()+ \
               self.enabled_.length()+self.di_.length()+self.do_.length()

    def serialize(self) -> bytes:
        return self.candev_head_.serialize() + self.profile_speed_.serialize()+ self.profile_acc_.serialize()+ \
               self.profile_dec_.serialize()+ self.status_.serialize()+ self.control_mode_.serialize()+ \
               self.command_velocity_.serialize()+ self.command_position_.serialize()+ self.command_current_.serialize()+ \
               self.enable_.serialize() + self.state_.serialize() + self.error_code_.serialize() + \
               self.time_stamp_.serialize()+ self.actual_velocity_.serialize()+ self.actual_position_.serialize()+ self.actual_current_.serialize()\
               +self.enabled_.serialize()+self.di_.serialize()+self.do_.serialize()

    def build(self, data, offset) -> int:
        offset = self.candev_head_.build(data, offset)
        offset = self.profile_speed_.build(data, offset)
        offset = self.profile_acc_.build(data, offset)
        offset = self.profile_dec_.build(data, offset)
        offset = self.status_.build(data, offset)
        offset = self.control_mode_.build(data, offset)
        offset = self.command_velocity_.build(data, offset)
        offset = self.command_position_.build(data, offset)
        offset = self.command_current_.build(data, offset)
        offset = self.enable_.build(data, offset)
        offset = self.state_.build(data, offset)
        offset = self.error_code_.build(data, offset)
        offset = self.time_stamp_.build(data, offset)
        offset = self.actual_velocity_.build(data, offset)
        offset = self.actual_position_.build(data, offset)
        offset = self.actual_current_.build(data, offset)
        offset = self.enabled_.build(data, offset)
        offset = self.di_.build(data, offset)
        return self.do_.build(data, offset)

class var__angle_encoder_t():
    def __init__(self):
        super(var__angle_encoder_t, self).__init__()
        self.candev_head_=var__can_device_t()
        self.angle_encoder_type_t=proto_uint32()
        self.state_=proto_int()
        self.actual_angle_=proto_int64()
        self.error_code_=proto_int()
        self.time_stamp_=proto_uint64()

    def length(self) -> int:
        return self.candev_head_.length() +  self.state_.length()+ self.error_code_.length()+ self.time_stamp_.length()

    def serialize(self) -> bytes:
        return self.candev_head_.serialize() + self.state_.serialize() + self.error_code_.serialize() + \
               self.time_stamp_.serialize()

    def build(self, data, offset) -> int:
        offset = self.candev_head_.build(data, offset)
        offset = self.state_.build(data, offset)
        offset = self.error_code_.build(data, offset)
        return self.time_stamp_.build(data, offset)

class var__dio_t():
    def __init__(self):
        super(var__dio_t, self).__init__()
        self.candev_head_=var__can_device_t()
        self.di_channel_num_=proto_int()
        self.do_channel_num_=proto_int()
        self.status_=var__status_describe_t()
        self.do_=proto_int()
        self.ao_=list()
        self.bus_state_=proto_int()
        self.error_code_=proto_int()
        self.time_stamp_=proto_uint64()
        self.enabled_=proto_int()
        self.di_=proto_int()
        self.ai_=dict()
        self.do2_=proto_int()
        self.ao2_=dict()

    def length(self) -> int:
        return self.candev_head_.length() +  self.di_channel_num_.length()+ self.do_channel_num_.length()+ self.status_.length()+ \
                self.do_.length()+ length_userdef_block(10)+ self.bus_state_.length()+  self.error_code_.length()+self.time_stamp_.length()+\
                self.enabled_.length()+  self.di_.length()+ length_userdef_block(10)+ self.do2_.length()+ length_userdef_block(10)


    def serialize(self) -> bytes:
        return self.candev_head_.serialize() + self.di_channel_num_.serialize() + self.do_channel_num_.serialize() + \
               self.status_.serialize()+self.do_.serialize() + serialize_userdef_block(self.ao_,16) + self.bus_state_.serialize() + \
               self.error_code_.serialize() + self.time_stamp_.serialize() + self.enabled_.serialize() + \
               self.di_.serialize() + serialize_userdef_block(self.ai_,16) +self.do2_.serialize()+ serialize_userdef_block(self.ao2_)

    def build(self, data, offset) -> int:
        offset = self.candev_head_.build(data, offset)
        offset = self.di_channel_num_.build(data, offset)
        offset = self.do_channel_num_.build(data, offset)
        offset = self.status_.build(data, offset)
        offset = self.di_.build(data,offset)
        (offset, self.ao_)=build_userdef_block(data, offset, 10)
        offset = self.bus_state_.build(data, offset)
        offset = self.error_code_.build(data, offset)
        offset = self.time_stamp_.build(data, offset)
        offset = self.enabled_.build(data, offset)
        offset = self.di_.build(data, offset)
        (offset, self.ai_) = build_userdef_block(data, offset, 10)
        offset = self.do2_.build(data, offset)
        (offset, self.ao2_) = build_userdef_block(data, offset, 10)
        return offset

class var__usrdef_buffer_t():
    def __init__(self):
        super(var__usrdef_buffer_t, self).__init__()
        self.usrbuf_=''

    def length(self) -> int:
        return 1024

    def serialize(self) -> bytes:
        return serialize_char(self.usrbuf_,1024)

    def build(self, data, offset) -> int:
        (offset,self.usrbuf_) = build_char(data,offset,1024)
        return offset

class var__swheel_t():
    def __init__(self):
        super(var__swheel_t, self).__init__()
        self.min_angle_=proto_double()
        self.max_angle_=proto_double()
        self.zero_angle_=proto_double()
        self.zero_angle_enc_=proto_int64()
        self.max_w_=proto_double()
        self.control_mode_=proto_uint32()
        self.scale_control_=proto_double()
        self.scale_feedback_=proto_double()
        self.control_cp_=proto_double()
        self.control_ci_=proto_double()
        self.control_cd_=proto_double()
        self.enabled_=proto_int()
        self.actual_angle_=proto_double()
        self.actual_angle_enc_=proto_int64()
        self.time_stamp_=proto_uint64()
        self.error_code_=proto_int()
        self.enable_=proto_int()
        self.command_angle_=proto_double()
        self.command_angle_enc_=proto_int64()
        self.command_rate_=proto_double()
        self.command_rate_enc_=proto_double()

    def length(self) -> int:
        return self.min_angle_.length()+self.max_angle_.length()+self.zero_angle_.length()+self.zero_angle_enc_.length()+ \
               self.max_w_.length()+self.control_mode_.length()+self.scale_control_.length()+self.scale_feedback_.length()+ \
               self.control_cp_.length()+self.control_ci_.length()+self.control_cd_.length()+self.enabled_.length()+ \
               self.actual_angle_.length()+self.actual_angle_enc_.length()+self.time_stamp_.length()+self.error_code_.length()+ \
               self.enable_.length()+self.command_angle_.length()+self.command_angle_enc_.length()+self.command_rate_.length()+self.command_rate_enc_.length()

    def serialize(self) -> bytes:
        return self.min_angle_.serialize()+self.max_angle_.serialize()+self.zero_angle_.serialize()+self.zero_angle_enc_.serialize()+ \
               self.max_w_.serialize()+self.control_mode_.serialize()+self.scale_control_.serialize()+self.scale_feedback_.serialize()+ \
               self.control_cp_.serialize()+self.control_ci_.serialize()+self.control_cd_.serialize()+self.enabled_.serialize()+ \
               self.actual_angle_.serialize()+self.actual_angle_enc_.serialize()+self.time_stamp_.serialize()+self.error_code_.serialize()+ \
               self.enable_.serialize()+self.command_angle_.serialize()+self.command_angle_enc_.serialize()+self.command_rate_.serialize()+self.command_rate_enc_.serialize()

    def build(self, data, offset) -> int:
        offset = self.min_angle_.build(data, offset)
        offset = self.max_angle_.build(data,offset)
        offset = self.zero_angle_.build(data, offset)
        offset = self.zero_angle_enc_.build(data, offset)
        offset = self.max_w_.build(data, offset)
        offset = self.control_mode_.build(data, offset)
        offset = self.scale_control_.build(data, offset)
        offset = self.scale_feedback_.build(data, offset)
        offset = self.control_cp_.build(data, offset)
        offset = self.control_ci_.build(data, offset)
        offset = self.control_cd_.build(data, offset)
        offset = self.enabled_.build(data, offset)
        offset = self.actual_angle_.build(data, offset)
        offset = self.actual_angle_enc_.build(data, offset)
        offset = self.time_stamp_.build(data, offset)
        offset = self.error_code_.build(data, offset)
        offset = self.enable_.build(data, offset)
        offset = self.command_angle_.build(data, offset)
        offset = self.command_angle_enc_.build(data, offset)
        offset = self.command_rate_.build(data, offset)
        return self.command_rate_enc_.build(data, offset)

class var__dwheel_t():
    def __init__(self):
        super(var__dwheel_t, self).__init__()
        self.max_speed_=proto_double()
        self.max_acc_=proto_double()
        self.max_dec_=proto_double()
        self.control_mode_=proto_uint32()
        self.scale_control_=proto_double()
        self.scale_feedback_=proto_double()
        self.roll_weight_=proto_double()
        self.slide_weight_=proto_double()
        self.enabled_=proto_int()
        self.actual_velocity_=proto_double()
        self.actual_velocity_enc_=proto_int64()
        self.actual_position_=proto_double()
        self.actual_position_enc_=proto_int64()
        self.actual_current_=proto_double()
        self.time_stamp_=proto_uint64()
        self.error_code_=proto_int()
        self.enable_=proto_int()
        self.command_velocity_=proto_double()
        self.command_velocity_enc_=proto_int64()
        self.command_position_=proto_double()
        self.command_position_enc_=proto_double()
        self.command_current_=proto_double()

    def length(self) -> int:
        return self.max_speed_.length()+self.max_acc_.length()+self.max_dec_.length()+self.control_mode_.length()+self.scale_control_.length()+ \
               self.scale_feedback_.length()+self.roll_weight_.length()+self.slide_weight_.length()+self.enabled_.length()+ \
               self.actual_velocity_.length()+self.actual_velocity_enc_.length()+self.actual_position_.length()+self.actual_position_enc_.length()+ \
               self.actual_current_.length()+self.time_stamp_.length()+self.error_code_.length()+self.enable_.length()+ \
               self.command_velocity_.length()+self.command_velocity_enc_.length()+self.command_position_.length()+self.command_position_enc_.length()+self.command_current_.length()

    def serialize(self) -> bytes:
        return self.max_speed_.serialize()+self.max_acc_.serialize()+self.max_dec_.serialize()+self.control_mode_.serialize()+self.scale_control_.serialize()+ \
               self.scale_feedback_.serialize()+self.roll_weight_.serialize()+self.slide_weight_.serialize()+self.enabled_.serialize()+ \
               self.actual_velocity_.serialize()+self.actual_velocity_enc_.serialize()+self.actual_position_.serialize()+self.actual_position_enc_.serialize()+ \
               self.actual_current_.serialize()+self.time_stamp_.serialize()+self.error_code_.serialize()+self.enable_.serialize()+ \
               self.command_velocity_.serialize()+self.command_velocity_enc_.serialize()+self.command_position_.serialize()+self.command_position_enc_.serialize()+self.command_current_.serialize()

    def build(self, data, offset) -> int:
        offset = self.max_speed_.build(data, offset)
        offset = self.max_acc_.build(data,offset)
        offset = self.max_dec_.build(data, offset)
        offset = self.control_mode_.build(data, offset)
        offset = self.scale_control_.build(data, offset)
        offset = self.scale_feedback_.build(data, offset)
        offset = self.roll_weight_.build(data, offset)
        offset = self.slide_weight_.build(data, offset)
        offset = self.enabled_.build(data, offset)
        offset = self.actual_velocity_.build(data, offset)
        offset = self.actual_velocity_enc_.build(data, offset)
        offset = self.actual_position_.build(data, offset)
        offset = self.actual_position_enc_.build(data, offset)
        offset = self.actual_current_.build(data, offset)
        offset = self.time_stamp_.build(data, offset)
        offset = self.error_code_.build(data, offset)
        offset = self.enable_.build(data, offset)
        offset = self.command_velocity_.build(data, offset)
        offset = self.command_velocity_enc_.build(data, offset)
        offset = self.command_position_.build(data, offset)
        offset = self.command_position_enc_.build(data, offset)
        return self.command_current_.build(data,offset)

class var__sdd_extra():
    def __init__(self):
        super(var__sdd_extra, self).__init__()
        self.gauge_=proto_double()

    def length(self)->int:
        return self.gauge_.length()

    def serialize(self)->bytes:
        return self.gauge_.serialize()

    def build(self,data,offset)->int:
        return self.gauge_.build(data,offset)


class st_safety_dev_bank_src_info():
    def __init__(self):
        super(st_safety_dev_bank_src_info, self).__init__()
        self.src_dev_id=proto_int()
        self.src_dev_type=proto_uint32()
        self.data_src_channel=list()
        self.dev_data_type=proto_uint32()
        self.reslut=proto_uint32()
        self.sensor_name=''
        self.ai_thres=proto_double()
        self.ai_cur=proto_double()

    def length(self)->int:
        return self.src_dev_id.length()+self.src_dev_type.length()+3*4+self.dev_data_type.length()+self.reslut.length()+\
                20+self.ai_thres.length()+self.ai_cur.length()

    def serialize(self)->bytes:
        return self.src_dev_id.serialize()+self.src_dev_type.serialize()+serialize_int(self.data_src_channel[0])+ \
               serialize_int(self.data_src_channel[1])+serialize_int(self.data_src_channel[2])+self.dev_data_type.serialize()+\
                self.reslut.serialize()+serialize_char(self.sensor_name,20)+self.ai_thres.serialize()+self.ai_cur.serialize()

    def build(self,data,offset)->int:
        offset=self.src_dev_id.build(data,offset)
        offset = self.src_dev_type.build(data, offset)
        (offset,self.data_src_channel)=build_int(data,offset,3)
        offset=self.dev_data_type.build(data,offset)
        offset=self.reslut.build(data,offset)
        (offset,self.sensor_name)=build_char(data,offset,20)
        if len(self.sensor_name) == 20 and self.sensor_name[0] == '\0':
            self.sensor_name = ""
        offset=self.ai_thres.build(data,offset)
        return self.ai_cur.build(data,offset)

class var__safety_t():
    def __init__(self):
        super(var__safety_t, self).__init__()
        self.enable_=proto_int()
        self.enabled_=proto_int()
        self.cur_bank_id_=proto_int()
        self.cur_bank_level=proto_int()
        self.safety_reslut_=proto_uint32()
        # self.sen=st_safety_dev_bank_src_info()
        self.sensor_trrigered_=st_safety_dev_bank_src_info()
        self.manual_bank_id_=proto_int()
        self.manual_bank_level_=proto_int()


    def length(self)->int:
        return self.enable_.length()+self.enabled_.length()+self.cur_bank_id_.length()+self.cur_bank_level.length()+\
                self.safety_reslut_.length()+self.sensor_trrigered_.length()+self.manual_bank_id_.length()+self.manual_bank_level_.length()

    def serialize(self)->bytes:
        return self.enable_.serialize()+self.enabled_.serialize()+self.cur_bank_id_.serialize()+self.cur_bank_level.serialize()+\
                self.safety_reslut_.serialize()+self.sensor_trrigered_.serialize()+self.manual_bank_id_.serialize()+self.manual_bank_level_.serialize()

    def build(self,data,offset)->int:
        offset = self.enable_.build(data, offset)
        offset = self.enabled_.build(data, offset)
        offset = self.cur_bank_id_.build(data, offset)
        offset = self.cur_bank_level.build(data, offset)
        offset = self.safety_reslut_.build(data, offset)
        offset = self.sensor_trrigered_.build(data, offset)
        offset = self.manual_bank_id_.build(data, offset)
        return self.manual_bank_level_.build(data,offset)
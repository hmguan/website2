from db import session_obj,user_info,file_list
from sqlalchemy import or_
from sqlalchemy import asc
from sqlalchemy import desc
import os
from datetime import datetime
from pynsp.logger import*
from configuration import config


class file_manager():
    def __init__(self):
        pass

    @staticmethod
    def insert(user_id,file_name,file_size):
        try:
            tmp = session_obj.query(user_info).filter_by(id=user_id).first()
            if(tmp ==None):
                return -1
            
            tmp = session_obj.query(file_list).filter_by(file_name=file_name).first()
            if(tmp !=None):
                return -2
            time = datetime.datetime.now()
            list_obj = file_list(user_id = user_id,file_name= file_name,file_size =file_size,time=time)
            session_obj.add(list_obj)
            session_obj.commit()
            return 0
        except Exception as e:
            Logger().get_logger().warning(str(e))
            return -3  
        
    
    @staticmethod
    def file_list(user_id):
        try:
            return session_obj.query(file_list).filter_by(user_id=user_id).order_by(desc(file_list.time)).all()
        except Exception as e:
            Logger().get_logger().warning(str(e))
            return -1 

    @staticmethod
    def remove(file_id):
        try:
            ret = session_obj.query(file_list).filter_by(id=file_id).first()
            if not ret:
                return -1

            tmp  = session_obj.query(file_list).get(ret.id)
            folder_path = config.ROOTDIR +tmp.user.username +config.BACKUPFILEDER
                        
            file_path = os.path.join(folder_path,tmp.file_name)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    Logger().get_logger().warning(str(e))
                return -2

            session_obj.delete(tmp)
            session_obj.commit()
            return 0
        except Exception as e:
            Logger().get_logger().warning(str(e))
            return -2
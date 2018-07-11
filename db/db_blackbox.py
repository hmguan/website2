
from db import session_obj,user_info,blackbox_temps
from sqlalchemy import or_
from sqlalchemy import asc
from sqlalchemy import desc
from configuration import config
import os
from datetime import datetime

class blackbox_manager():
    def __init__(self):
        pass
    
    @staticmethod
    def insert_temps(user_id,name,temps_types,others):
        tmp = session_obj.query(user_info).filter_by(id=user_id).first()
        if(tmp ==None):
            return -1
        
        temps_obj = blackbox_temps(user_id = user_id,name=name,temps_types= temps_types,others=others,time=datetime.now())
        session_obj.add(temps_obj)
        session_obj.commit()
        return temps_obj.id


    @staticmethod
    def temps(user_id):
        return session_obj.query(blackbox_temps).filter_by(user_id=user_id).order_by(desc(blackbox_temps.time)).all()
    

    @staticmethod
    def remove_temps(temps_id):
        ret = session_obj.query(blackbox_temps).filter_by(id=temps_id).first()
        if not ret:
            return -1

        tmp  = session_obj.query(blackbox_temps).get(ret.id)

        session_obj.delete(tmp)
        session_obj.commit()
        return 0
    

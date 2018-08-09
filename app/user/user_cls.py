
import errtypes
import base64
import random
import time
from threading import Thread,RLock
from db.db_users import user
import copy

class user_cls():
    def __init__(self,user_name,pwd):
        self.user_name = user_name
        self.pwd = pwd
        self.user_id = -1
        self.user_type ='guest'
        self.u_uuid = ''
        self.token=''

    #用户登录
    def login(self)->dict:
        (user_id, user_type) = user.verification(self.user_name,self.pwd)
        if user_id < 0:
            return user_id
        self.user_id = user_id
        self.user_type = user_type
        return user_id
    




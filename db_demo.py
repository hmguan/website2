

from db.db_users import user
from app.user.userview import users_center
import ptvsd
import base64
import random
import time
from db.db_package import package_manager

#远程调试
ptvsd.settrace(None, ('0.0.0.0', 2345))
#ptvsd.wait_for_attach()

def main():

    ret = user.append('gz','e10adc3949ba59abbe56e057f20f883e','r')
    ret = user.append('robot','e10adc3949ba59abbe56e057f20f883e','r')

    
    ret = package_manager.query_packages(1)
    print(ret.id)

    print(ret)

if __name__ == "__main__":
    main()

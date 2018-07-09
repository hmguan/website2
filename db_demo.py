
#from hdfs import Client
from db.db_logger import login_manager
from datetime import datetime



def main():
#    client = Client("http://hadoop100:50070")
#    print(client)
#    print(client.status("/",strict=True))

#    print('-----------------------------')
#    print(client.list("/user/stefan"))
    filename ='sss'
    login_manager.insert(1,login_type='packages',time =datetime.now(),msg="upload file:",u_uuid='')
if __name__ == "__main__":
    main()

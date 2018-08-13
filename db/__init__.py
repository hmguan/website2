# author:stefan
# data:2018/5/11 14:20


from sqlalchemy import create_engine
from sqlalchemy import String,Integer,Column,Table,MetaData,ForeignKey,Enum,DateTime
from sqlalchemy.orm import mapper,sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = create_engine('sqlite:///db/db_users.db',connect_args={'check_same_thread': False},encoding='utf-8')
Base = declarative_base()


SQL_STRING_LEN =  256
#用户表
class user_info(Base):
    __tablename__ = 'users'  
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(258),nullable=False)                
    pwd= Column(String(258),nullable=False)                     
    identity_type= Column(Enum('admin','guest'),nullable=False)
    user_path = Column(String(12),nullable=False)
    permission =  Column(Enum('r','w','wr'),nullable=False)

#别名
class group_alias_info(Base):
    __tablename__ = 'group_alias'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer,ForeignKey('users.id'),nullable=False)
    name = Column(String(256),nullable=False)
    alias = Column(String(256),nullable=True)

#升级包管理
class package_info(Base):
    __tablename__ = 'packages'
    id= Column(Integer,primary_key = True,autoincrement=True)
    user_id = Column(Integer,ForeignKey('users.id'),nullable=False)
    version = Column(String(256),nullable = False)
    package_name = Column(String(256),nullable=False)
    time = Column(DateTime,nullable=True)
    remarks = Column(String(256),nullable=True)
    user = relationship("user_info", foreign_keys=[user_id])


class logger(Base):
    __tablename__ = 'logger'
    id= Column(Integer,primary_key = True,autoincrement=True)
    user_id = Column(Integer,ForeignKey('users.id'),nullable=False)
    login_type = Column(Enum('online','offline','packages','bin'),nullable = False)
    msg = Column(String(256),nullable=False)
    u_uuid = Column(String(256),nullable=True)
    time = Column(DateTime,nullable=False)
    remarks = Column(String(256),nullable=True)


#黑盒子日志模板
class blackbox_temps(Base):
    __tablename__ = 'bk_temps'
    id= Column(Integer,primary_key = True,autoincrement=True)
    name =  Column(String(256),nullable=False)
    user_id = Column(Integer,ForeignKey('users.id'),nullable=False)
    temps_types = Column(String(256),nullable=False)
    others = Column(String(256),nullable=True)
    time = Column(DateTime,nullable=False)


class file_list(Base):
    __tablename__ = 'file_list'
    id= Column(Integer,primary_key = True,autoincrement=True)
    file_name =  Column(String(256),nullable=False)
    user_id = Column(Integer,ForeignKey('users.id'),nullable=False)
    file_size = Column(String(256),nullable=False)
    time = Column(DateTime,nullable=False)
    user = relationship("user_info", foreign_keys=[user_id])

Base.metadata.create_all(engine) 
session_cls =sessionmaker(bind=engine)
session_obj = session_cls()

#初始化数据库root
ret = session_obj.query(user_info).filter_by(username='root').first()
if(ret ==None):
    user_obj = user_info(username='root',pwd='e10adc3949ba59abbe56e057f20f883e',identity_type='admin',user_path='/',permission = 'wr')
    session_obj.add(user_obj)
    session_obj.commit()





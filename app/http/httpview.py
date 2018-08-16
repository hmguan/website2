import flask
from flask import jsonify
from flask import Flask,render_template,request, session
import errtypes
from . import http_main
from db.db_users import user
from app.user.user_service_agant import users_center
from app.configuration.configapi import get_config_path
import os,datetime
from db.db_package import package_manager
from pynsp.logger import *
import os
import httpRequestCode
from .httpreq import *
import ptvsd
ptvsd.settrace(None, ('0.0.0.0', 1234))

def is_file_open(file_path):
    is_opened = is_open(file_path)
    Logger().get_logger().info('file_path:{0}, is_open:{1}'.format(file_path,is_opened))
    return is_opened

def get_all_pid():
    #获取当前所有进程
    return [_i for _i in os.listdir('/proc') if _i.isdigit()]

def is_open(file_path) ->bool:
    if file_path.startswith('./'):
        file_path = os.path.abspath(file_path)
    for pid in get_all_pid():
        _fd_dir = '/proc/{pid}/fd'.format(pid = pid)
        if os.access(_fd_dir, os.R_OK) == False:
            continue

        for fd in os.listdir(_fd_dir):
            fd_path = os.path.join(_fd_dir, fd)
            if os.path.exists(fd_path) and os.readlink(fd_path) == file_path:
                return True
    return False

@http_main.route('/upload' ,methods=['GET' ,'POST'])
def upload_file():
    print(request.files)
    if request.method == 'POST':
        print('recv file local')
        if 'file' not in request.files:
            return jsonify({'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament})
        file =request.files['file']
        if file.filename == '':
            return jsonify({'code': errtypes.HttpResponseCode_NOFILE, 'msg': errtypes.HttpResponseCodeMsg_NoFileSelect})
        else:
            filename = file.filename
            try:
                if file:
                    login_token = request.form['login_token']
                    
                    json_data = get_user_id(login_token)
                    if json_data.get('code') != 0:
                        return jsonify({'code': json_data.get('code'),
                                        'msg': json_data.get('msg')})
                    
                    user_id = json_data.get('user_id')
                    (ret,user_name) = user.query_name_by_id(user_id)
                    if -1==ret:
                        return jsonify({'code': errtypes.HttpResponseCode_UserNotExisted, 'msg': errtypes.HttpRequestMsg_UserNotExisted})
                    if -2==ret:
                        return jsonify({'code': errtypes.HttpResponseCode_Sqlerror, 'msg': errtypes.HttpResponseCodeMsg_Sqlerror})
                    
                    if user_name is None:
                        Logger().get_logger().error('can not find user by user_id = {}'.format(user_id))
                        return jsonify({'code': errtypes.HttpResponseCode_UserNotExisted, 'msg': errtypes.HttpRequestMsg_UserNotExisted})
                    
                    version = request.form['version']
                    remark =request.form['remark']
                    folder_path = get_config_path(user_name,httpRequestCode.HttpRequestFileType_Patch)
                    if os.path.exists(folder_path) == False:
                        os.makedirs(folder_path)
                    file_path = os.path.join(folder_path, filename)

                    #The judgment is open only when the file exists
                    if os.path.exists(file_path) and is_file_open(file_path):
                        return jsonify({'code': errtypes.HttpResponseCode_FileBusy, 'msg': errtypes.HttpResponseMsg_FileBusy})
                    file.save(file_path)
                    time = datetime.datetime.now()
                    ret = package_manager.upload(user_id, filename, version, time, remark)
                    if ret == -1:
                        return jsonify({'code': errtypes.HttpResponseCode_UserNotExisted, 'msg': errtypes.HttpRequestMsg_UserNotExisted})
                    if ret == -2:
                        return jsonify({'code': errtypes.HttpResponseCode_Sqlerror, 'msg': errtypes.HttpResponseCode_Sqlerror})
                    return jsonify({'code': errtypes.HttpResponseCode_Normal, 'msg': errtypes.HttpResponseMsg_Normal})
            except Exception as e:
                return jsonify({'code': errtypes.HttpResponseCode_UPLOADEXCEPTIONERROR, 'msg': str(e)})

from flask import send_file, send_from_directory
from flask import make_response

@http_main.route("/download/<path:url_fileinfo>", methods=['GET'])
def download_file(url_fileinfo):
    #取出url中的扩展信息 user_id=，type= 
    [extern_info,filepath]=url_fileinfo.split('/',1)
    #取出文件名和路径
    [dirname,filename]=os.path.split(filepath)
    data = extern_info.split(',',1)
    if len(data) <2:
        Logger().get_logger().error('Incorrectly formatting')
        return make_response(jsonify({'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament}),404)
    
    userinfo = data[0].split('=',1)
    type_info = data[1].split('=',1)
    if len(userinfo) < 2 or len(type_info) <2:
        Logger().get_logger().error('Incorrectly formatting {}:{}'.format(data[0],data[1]))
        return make_response(jsonify({'code': errtypes.HttpResponseCode_InvaildParament, 'msg': errtypes.HttpResponseMsg_InvaildParament}),404)

    json_data = get_user_id(userinfo[1])
    if json_data.get('code') != 0:
        Logger().get_logger().error('login_token {}:{}'.format(json_data.get('code'),json_data.get('msg')))
        return make_response(jsonify({'code': json_data.get('code'), 'msg': json_data.get('msg')}),404)

    user_id = json_data.get('user_id')
    (ret,user_name) = user.query_name_by_id(user_id)
    if -1==ret:
        return jsonify({'code': errtypes.HttpResponseCode_UserNotExisted, 'msg': errtypes.HttpRequestMsg_UserNotExisted})
    if -2==ret:
        return jsonify({'code': errtypes.HttpResponseCode_Sqlerror, 'msg': errtypes.HttpResponseCodeMsg_Sqlerror})
    
    if user_name is None:
        Logger().get_logger().error('can not find user by user_id = {}'.format(int(userinfo[1])))
        return make_response(jsonify({'code': errtypes.HttpResponseCode_UserNotExisted, 'msg': errtypes.HttpResponseCodeMsg_UserNotExisted}),404)

    type_id = int(type_info[1])
    try:
        directory = get_config_path(user_name,type_id)
        if directory.startswith('./'):
            directory = os.path.abspath(directory)
        
        file_path = os.path.join(directory, dirname)

        if os.path.exists(file_path+'/'+filename) is False :
            Logger().get_logger().error('file  not exist path= {}'.format(file_path))
            return make_response(jsonify({'code': errtypes.HttpResponseCode_FileNotExist, 'msg': errtypes.HttpResponseMsg_FileNotExist}),404)

        response = make_response(send_from_directory(file_path, filename, as_attachment=True))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
        return response
    except Exception as e:
        raise e

@http_main.route("/download_path/<path:filename>", methods=['GET'])
def download(filename):
    [dirname,name]=os.path.split(filename)
    if dirname.startswith('/') is False:
        dirname = '/' + dirname
    response = make_response(send_from_directory(dirname, name, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(name.encode().decode('latin-1'))
    return response

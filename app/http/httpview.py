import flask
from flask import jsonify
from flask import Flask,render_template,request, session
import errtypes
from . import http_main
from db.db_users import user
from configuration import get_config_path
import os,datetime
from db.db_package import package_manager
from pynsp.logger import *
import os

def status(file_path):
    open_fd_list = get_all_fd(file_path)
    open_count = len(open_fd_list)
    Logger().get_logger().info('file_path:{0}, open_count:{1}'.format(file_path,open_count))
    is_opened = False
    if open_count > 0:
        is_opened = True
    return is_opened

def get_all_pid():
    """获取当前所有进程"""
    return [_i for _i in os.listdir('/proc') if _i.isdigit()]

def get_all_fd(file_path):
    """获取所有已经打开该文件的fd路径"""
    all_fd = []
    if file_path.startswith('./'):
        file_path = os.path.abspath(file_path)
    for pid in get_all_pid():
        _fd_dir = '/proc/{pid}/fd'.format(pid = pid)
        if os.access(_fd_dir, os.R_OK) == False:
            continue

        for fd in os.listdir(_fd_dir):
            fd_path = os.path.join(_fd_dir, fd)
            if os.path.exists(fd_path) and os.readlink(fd_path) == file_path:
                all_fd.append(fd_path)
    return all_fd

@http_main.route('/upload' ,methods=['GET' ,'POST'])
def upload_file():
    print(request.files)
    if request.method == 'POST':
        print('recv file local')
        if 'file' not in request.files:
            return jsonify({'code': errtypes.HttpResponseCode_InvaildParament, 'msg': '参数有误'})
        file =request.files['file']
        if file.filename == '':
            return jsonify({'code': errtypes.HttpResponseCode_NOFILE, 'msg': '未选文件'})
        else:
            filename = file.filename
            try:
                if file:
                    user_id = request.form['user_id']
                    user_name = user.query_name_by_id(user_id)
                    if user_name is None:
                        Logger().get_logger().error('can not find user by user_id = {}'.format(user_id))
                        return jsonify({'code': errtypes.HttpResponseCode_UserNotExisted, 'msg': 'can not find user'})

                    version = request.form['version']
                    remark =request.form['remark']
                    folder_path = get_config_path(user_name,errtypes.HttpRequestFileType_Patch)

                    if os.path.exists(folder_path) == False:
                        os.makedirs(folder_path)
                    file_path = os.path.join(folder_path, filename)

                    #The judgment is open only when the file exists
                    if os.path.exists(file_path) and status(file_path):
                        return jsonify({'code': errtypes.HttpResponseCode_FileBusy, 'msg': errtypes.HttpResponseMsg_FileBusy})
                    
                    file.save(file_path)
                    time = datetime.datetime.now()
                    ret = package_manager.upload(request.form['user_id'], filename, version, time, remark)
                    if ret == -1:
                        return jsonify({'code': errtypes.HttpResponseCode_UserNotExisted, 'msg': '上传失败，用户不存在'})

                    return jsonify({'code': 0, 'msg': '上传成功'})
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
        return '',404
    
    userinfo = data[0].split('=',1)
    type_info = data[1].split('=',1)
    if len(userinfo) < 2 or len(type_info) <2:
        Logger().get_logger().error('Incorrectly formatting {}:{}'.format(data[0],data[1]))
        return '',404

    user_name = user.query_name_by_id(int(userinfo[1]))
    if user_name is None:
        Logger().get_logger().error('can not find user by user_id = {}'.format(user_id))
        return '',404

    type_id = int(type_info[1])

        # return jsonify({'code': errtypes.HttpResponseCode_UserNotExisted, 'msg': 'can not find user'})
    try:
        directory = get_config_path(user_name,type_id)
        if directory.startswith('./'):
            directory = os.path.abspath(directory)
        
        file_path = os.path.join(directory, dirname)

        if os.path.exists(file_path+'/'+filename) is False :
            Logger().get_logger().error('file  not exist path= {}'.format(file_path))
            return 'file could not find',404

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

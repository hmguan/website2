import flask
from flask import jsonify
from flask import Flask,render_template,request, session
import errtypes
from . import http_main
from db.db_users import user
from configuration import config
import os,datetime
from db.db_package import package_manager

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
                    version = request.form['version']
                    remark =request.form['remark']
                    user_name = user.query_name_by_id(request.form['user_id'])
                    folder_path = config.ROOTDIR +user_name + config.PATCHFOLDER

                    if os.path.exists(folder_path) == False:
                        os.makedirs(folder_path)
                    file_path = os.path.join(folder_path, filename)

                    file.save(file_path)
                    time = datetime.datetime.now()
                    ret = package_manager.upload(request.form['user_id'], filename, version, time, remark)
                    if ret == -1:
                        return jsonify({'code': errtypes.HttpResponseCode_UserNotExisted, 'msg': '上传失败，用户不存在'})

                    return jsonify({'code': 0, 'msg': '上传成功'})
            except Exception as e:
                return jsonify({'code': errtypes.HttpResponseCode_UPLOADEXCEPTIONERROR, 'msg': '上传失败'})
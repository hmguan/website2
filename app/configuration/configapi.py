from configuration import config
import os
import httpRequestCode

def get_config_path(user_name,file_type):
    config_path = ''
    if file_type == httpRequestCode.HttpRequestFileType_Patch:
        config_path = config.PATCHFOLDER
    elif file_type == httpRequestCode.HttpRequestFileType_BlackBox:
        config_path = config.BLACKBOXFOLDER
    elif file_type == httpRequestCode.HttpRequestFileType_Bin:
        config_path = config.BINFOLDER
    else:
        pass

    return config.ROOTDIR +user_name + config_path
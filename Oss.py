# -*- coding: utf-8 -*-
# author: xiaoming
# date: 2020/8/11

import oss2
import configparser
# 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
conf = configparser.ConfigParser()
conf_path = "DcmConfig.ini"
conf.read(conf_path)
Ackid = conf.get("oss",'Ackid')
Acksecret = conf.get("oss",'Acksecret')
Bucket = conf.get("oss","Bucket")
Endpoint = conf.get("oss","Endpoint")
Expires = conf.get('oss',"Expires")
def UploadPatientData(OssDir,LocalFile):
    auth = oss2.Auth(Ackid, Acksecret)
    bucket = oss2.Bucket(auth, Endpoint, Bucket)
    bucket.put_object_from_file(OssDir,LocalFile)

def GetTempAddress(OssObject):
    auth = oss2.Auth(Ackid, Acksecret)
    bucket = oss2.Bucket(auth, Endpoint, Bucket)
    ossobject = OssObject
    return(bucket.sign_url('GET',ossobject,int(Expires)))




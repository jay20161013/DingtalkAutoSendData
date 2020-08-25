# -*- encoding:utf-8 -*-
import pymysql
import hashlib
import configparser
import os
import sys
import wget
import ssl
from Dingtalk import GetDingTalkFormInfo

ssl._create_default_https_context = ssl._create_unverified_context

conf = configparser.ConfigParser()
conf_path = "DcmConfig.ini"
conf.read(conf_path)
#mysql
h = conf.get("mysql_conf","h")
u = conf.get("mysql_conf","u")
p = conf.get("mysql_conf","p")
hospitaldb = conf.get("mysql_conf","hospitaldb")
dicomdb = conf.get("mysql_conf","dicomdb")


def DownloadPatientDcm(Filmno,DownloadDir):
    db = pymysql.connect(h,u,p,dicomdb)
    cursor = db.cursor()
    cursor.execute("this is a sql for select url")
    result = cursor.fetchall()
    #print(result)
    for dcmurl in result:
        print(dcmurl[0])
        wget.download(dcmurl[0], DownloadDir)



# 查找影像号，返回元组
def GetFilmno(TaskId,PatientName):
    start_and_end_time = GetDingTalkFormInfo(TaskId)['["订单起始日期","订单终止日期"]']
    StartTime = start_and_end_time.split('"')[1]
    EndTime = start_and_end_time.split('"')[3]
    #print(PatientName,StartTime,EndTime)
    db = pymysql.connect(h,u,p,hospitaldb)
    cursor = db.cursor()
    cursor.execute("this is a sql for select filmno")
    Filmno = cursor.fetchall()
    return Filmno


def GetBodyItem(Filmno):
    db = pymysql.connect(h, u, p, hospitaldb)
    cursor = db.cursor()
    cursor.execute("this is a sql for select bodyitem")
    BodyItem = cursor.fetchall()
    return BodyItem[0][0]

def IsAgentDoctor(DoctorName):
    db = pymysql.connect(h, u, p, hospitaldb)
    cursor = db.cursor()
    cursor.execute("this is a sql for select agent doctor")
    agent_name = cursor.fetchall()
    return agent_name



# -*- coding: utf-8 -*-
# author: xiaoming
# date: 2020/8/7
import os
import requests
import json
import configparser
from NameToEmail import Name2Email
conf = configparser.ConfigParser()
conf_path = "DcmConfig.ini"
conf.read(conf_path)


dingtalk = conf.get("dingtalk","dingtalkoapi")
GetTokenIf = conf.get("dingtalk","GetTokenIf")
Appkey = conf.get("dingtalk","Appkey")
AppSecret = conf.get("dingtalk","AppSecret")
headers = {"Content-Type": "application/json"}
process_code = conf.get('dingtalk','ProcessCode')
#获取accesstoken
requests_access_token = requests.get("%s?appkey=%s&appsecret=%s" %(GetTokenIf,Appkey,AppSecret))
access_token = requests_access_token.json()["access_token"]
task_list = conf.get('Global','TaskList')
email_cache = conf.get('Global','EmailCache')
#print(process_code)
#获取审批列表
def GetTaskList():
    GetTaskListIf = "topapi/processinstance/listids"
    url = '%s/%s?access_token=%s' %(dingtalk,GetTaskListIf,access_token)
    data = {
        "process_code": process_code,
        "start_time": "1594090957"
    }

    datajson = json.dumps(data)
    r = requests.post(url, data=datajson, headers=headers)
    TaskList = r.json()['result']['list']
    return TaskList

#获取审批详情
def GetTaskInfo(TaskId):
    GetTaskInfo = "topapi/processinstance/get"
    url = '%s/%s?access_token=%s' % (dingtalk, GetTaskInfo, access_token)
    data = {"process_instance_id":"%s" %TaskId}
    datajson = json.dumps(data)
    r = requests.post(url, data=datajson, headers=headers)
    TaskInfo = r.json()
    return TaskInfo


# 获取表单中的信息
def GetDingTalkFormInfo(TaskId):
    dingtalk_form_dict = {}
    dingtalk_request = GetTaskInfo(TaskId)
    dingtalk_form = dingtalk_request['process_instance']['form_component_values']
    dingtalk_task_status = dingtalk_request['process_instance']['status']
    dingtalk_task_result = dingtalk_request['process_instance']['result']
    dingtalk_originator_userid = dingtalk_request['process_instance']['originator_userid']

    for i in dingtalk_form:
        k = i['name']
        v = i['value']
        dingtalk_form_dict[k] = v
    dingtalk_form_dict['task_result'] = dingtalk_task_result
    dingtalk_form_dict['task_status'] = dingtalk_task_status
    dingtalk_form_dict['dingtalk_originator_userid'] = dingtalk_originator_userid
    return dingtalk_form_dict


# 获取当前任务列表
def GetNowTaskList():
    if os.path.isfile(task_list) == False:
        task_list_file = open(task_list, mode="w", encoding="utf-8")
        task_list_file.close()
    listout = []
    for line in open(task_list, 'r'):
        line = line.strip('\n')
        listout.append(line)
    return listout


# 更新当然任务列表
def UpdateNowTaskList(TaskId):
    TaskList = open(task_list,'a')
    TaskList.write(TaskId+"\n")
    TaskList.close()

# 写邮件
def WriteEmail(Content):
    TaskList = open(email_cache,'a')
    TaskList.write(Content+"\n")
    TaskList.close()

# 对比找出新提交的审批
def DiffTask():
    Task = list(set(GetTaskList()).difference(set(GetNowTaskList())))
    return Task


# 获取发起人的名字
def GetOriginName(TaskId):
    originId = GetDingTalkFormInfo(TaskId)['dingtalk_originator_userid']
    url = '%s/user/get?access_token=%s&userid=%s' %(dingtalk,access_token,originId)
    r = requests.get(url,headers=headers)
    TaskInfo = r.json()
    return(TaskInfo['name'])

#获取审批发起者的邮件
def GetEmail(TaskId):
    name_cn = GetOriginName(TaskId)
    emial_address = Name2Email(name_cn)
    return emial_address


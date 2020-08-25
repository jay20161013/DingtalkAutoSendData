# -*- coding: utf-8 -*-
# author: xiaoming
# date: 2020/8/10
import os
import configparser
import time
import logging
import shutil
from Dingtalk import DiffTask
from Dingtalk import UpdateNowTaskList
from Dingtalk import WriteEmail
from Dingtalk import GetEmail
from Dingtalk import GetDingTalkFormInfo
from Dingtalk import GetOriginName
from DownloadDcm import GetFilmno
from DownloadDcm import DownloadPatientDcm
from DownloadDcm import GetBodyItem
from DownloadDcm import IsAgentDoctor
from Oss import UploadPatientData
from Oss import GetTempAddress
from SendMail import SendEmail


#配置文件初始化
conf = configparser.ConfigParser()
conf_path = "DcmConfig.ini"
conf.read(conf_path)


#日志初始化
#级别：info、debug、warning、error

DingTalkLog = conf.get("Global","DingTalkLog")
logger = logging.getLogger(__name__)
logger.setLevel(level = logging.DEBUG)
handler = logging.FileHandler(DingTalkLog)
#handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
DicomDir = conf.get("Global","DicomDir")
Today = time.strftime("%Y/%m/%d", time.localtime())
OssAddress = conf.get('oss','Address')
EmailCache = conf.get('Global','EmailCache')

# 拿出新提交的审批
DiffTask = DiffTask()
if len(DiffTask) == 0:
    logger.info('没有新的审批')
    exit(200)
else:
    logger.info('发现新的审批。开始处理')
    # 遍历新发现的审批
    for TaskId in DiffTask:
        # 先拿出发起人
        origin_name = GetOriginName(TaskId)
        # 获取导出方式
        export_method = GetDingTalkFormInfo(TaskId)['导出方式']
        # 判断导出方式如果不是"后台统导出"就退出
        if export_method != '后台系统导出':
            logger.info('该审批不线上审批，无需后台处理。 '
                        '审批ID:%s 导出方式:%s 发起人:%s' %(TaskId,export_method,origin_name))
            # 这个函数是把当前TaskID给存到文件里，下次比对就不管了
            UpdateNowTaskList(TaskId)
            exit(200)
        # 获取钉钉审批状态和结果
        task_status = GetDingTalkFormInfo(TaskId)['task_status']
        task_result = GetDingTalkFormInfo(TaskId)['task_result']
        if task_status == 'TERMINATED':
            logger.info('审批终止了 TaskID:%s' %TaskId)
            UpdateNowTaskList(TaskId)
            exit(30)
        if task_status == 'COMPLETED':
            if task_result != 'agree':
                logger.debug('审批被拒绝 TaskId:%s 发起人:%s' %(TaskId,origin_name))
                UpdateNowTaskList(TaskId)
                exit(21)
            else:
                logger.info('审批同意，开始执行脚本 TaskId:%s 发起人:%s' %(TaskId,origin_name))
            try:
                # 获取审批人的邮箱
                OriginEmail = GetEmail(TaskId)
            except:
                logger.error('获取审批发起人Email地址失败 TaskId:%s 发起人%s' %(TaskId,origin_name))
                UpdateNowTaskList(TaskId)
                exit(11)
            # 先判断医生是否和销售关联
            doctor_name = GetDingTalkFormInfo(TaskId)['出单医生姓名']
            agent_name = GetOriginName(TaskId)
            if len(IsAgentDoctor(doctor_name)) == 0:
                logger.error('该医生不属于任何销售。任务ID:%s 医生:%s 销售:%s 发起人:%s'
                             % (TaskId, doctor_name, agent_name,origin_name))
                SendEmail(OriginEmail, '该医生不属于任何销售 销售:%s 医生:%s'
                          %(doctor_name,agent_name), '获取数据异常' )
                UpdateNowTaskList(TaskId)
                exit(16)
            if IsAgentDoctor(doctor_name)[0][0] != agent_name:
                logger.error('医生销售无关 任务ID:%s 医生:%s 销售:%s 发起人:%s'
                             %(TaskId, doctor_name, agent_name,origin_name))
                SendEmail(OriginEmail, '医生:%s 不是销售:%s 的代理医生' % (doctor_name, agent_name),
                          '获取数据异常')
                UpdateNowTaskList(TaskId)
                exit(17)
            logger.info('开始处理审批:%s 发起人:%s' %(TaskId,origin_name))
            # 先清邮件缓存
            if os.path.isfile(EmailCache):
                os.remove(EmailCache)
            # 写标题
            WriteEmail("以下是患者数据，有效期是72小时。<br />")
            try:
                # 获取患者姓名
                GtPatientsName = GetDingTalkFormInfo(TaskId)['患者姓名']
            except:
                logger.error('获取任务ID:%s患者姓名异常 发起人:%s' %(TaskId,origin_name))
                UpdateNowTaskList(TaskId)
                exit(12)
            # 患者姓名是空格分开的，可能有多个患者
            PatientsName = ' '.join(GtPatientsName.split())
            PatientsNameList = PatientsName.split(' ')
            # 遍历取出的患者姓名
            for PatientName in PatientsNameList:
                # 获取影像号，返回的元组，多个可能
                Filmno = GetFilmno(TaskId,PatientName)
                if len(Filmno) == 0:
                    logger.error('影像号获取异常 TaskId:%s 患者:%s '
                                 ' 发起人:%s ' %(TaskId,PatientName,origin_name))
                    WriteEmail('患者:%s 没有查到影像号' %PatientName)
                    continue
                PatientDir = '%s/%s'%(DicomDir,PatientName)
                if os.path.isdir(PatientDir) == False:
                    os.mkdir(PatientDir)
                # 遍历患者影像号
                for F in Filmno:
                    # 返回的每个影像号都是一个元组，这里给他解开
                    Fo = F[0]
                    # 获取检查项目
                    body_item = GetBodyItem(Fo)
                    patient_dir_filmno = '%s/%s/%s_%s/' % (DicomDir, PatientName,
                                                          Fo ,body_item)
                    if os.path.isdir(patient_dir_filmno) == False:
                        os.mkdir(patient_dir_filmno)
                    try:
                        logger.info('患者姓名：%s 影像号：%s 开始下载。' % (PatientName, Fo))
                        DownloadPatientDcm(Fo,patient_dir_filmno)
                        logger.info('患者姓名：%s 影像号：%s 下载完成。' %(PatientName, Fo))
                    except:
                        logger.error('患者姓名：%s 影像号：%s 下载失败。 发起人:%s' %(PatientName,Fo,origin_name))
                        exit(14)

                # 切换到dicom工作目录
                os.chdir(DicomDir)
                dir_name = DicomDir+'/'+PatientName
                try:
                    shutil.make_archive(dir_name, 'zip', dir_name)
                    logger.info('%s 压缩成功,开始上传' % PatientName)
                    LocalFile = '%s.zip' % PatientDir
                    OssDir = '%s/%s.zip' % (Today, PatientName)
                except:
                    logger.error('压缩失败 患者:%s 发起人:%s' %(PatientName,origin_name))
                    exit(14)

                try:
                    # 上传患者数据到oss
                    UploadPatientData(OssDir,LocalFile)
                    logger.info('%s 上传完成' %PatientName)
                except:
                    logger.error('上传失败 (UploadPatientData函数报错)'
                                 ' 患者:%s 发起人:%s' %(PatientName,origin_name))
                    # 写邮件
                #email_url = OssAddress+OssDir
                email_url = GetTempAddress(OssDir)
                email_content = '<p><a href="%s">点击下载患者 %s 的影像数据</a></p>' \
                                %(email_url,PatientName)
                WriteEmail(email_content)
                # 删除临时文件
                logger.info('删除患者临时文件 患者:%s' %PatientName)
                os.system('rm -rf %s*' %PatientName)
        else:
            # 审批还在进行就退出脚本不发邮件
            logger.info('审批还在进行中 TaskId:%s 发起人:%s' %(TaskId,origin_name))
            #print('审批还在进行中')
            exit(200)

        # 发邮件
        WriteEmail("</br>----</br>author by：xiaoming")
        f = open(EmailCache, "r", encoding='UTF-8')
        str = f.read()
        f.close()
        try:
            title = Today+'患者数据'
            SendEmail(OriginEmail, str,title)
            logger.info('%s 发送邮件成功.' %PatientName)
        except:
            logger.error('邮件发送失败 患者:%s 任务ID:%s 发起人:%s' %(TaskId,PatientName,origin_name))
        # 把完成的ID加到文件里去
        UpdateNowTaskList(TaskId)


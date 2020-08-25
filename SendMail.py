# -*- coding: utf-8 -*-
# author: xiaoming
# date: 2020/8/11

# !/usr/bin/python3
import configparser
import smtplib
from email.mime.text import MIMEText
from email.header import Header
conf = configparser.ConfigParser()
conf_path = "DcmConfig.ini"
conf.read(conf_path)

mail_host = conf.get('Email','mail_host')
mail_user = conf.get('Email','mail_user')
mail_pass = conf.get('Email','mail_pass')

# SendEmail(接收者，邮件内容)
def SendEmail(receivers,content,title):
    sender = mail_user
    #message = MIMEText(Content, 'plain', 'utf-8')
    message = MIMEText(content, 'html', 'utf-8')
    message['From'] = Header('同心患者数据', 'utf-8')
    #message['to'] = Header('qcc', 'utf-8')
    subject = title
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host,465)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")


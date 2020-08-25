## usage
requirements.txt:
logging oss2 configparser xpinyin wget pymysql


python3 main.py

----

#### main.py
主模块

#### Dingtalk.py
包含了一大堆关于钉钉的函数

#### DownloadDcm.py
用来查数据库和下载患者数据

#### Oss.py
调用Oss SDK来上传患者数据

#### SendMail.py 
发邮件用的

#### NameToEmail.py
把姓名拼接成电子邮件

#### DcmConfig.ini
配置文件

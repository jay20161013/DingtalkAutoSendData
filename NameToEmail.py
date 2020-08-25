# -*- coding: utf-8 -*-
# author: xiaoming
# date: 2020/8/14
from xpinyin import Pinyin
p = Pinyin()

def Name2Email(myname):
    tmp_namelist = []
    final_namelist = []
    for name in myname:
        tmp_namelist.append(name)
    firstname = p.get_pinyin(tmp_namelist[0])
    #把姓加到列表里
    final_namelist.append(firstname)
    #给姓删了
    tmp_namelist.pop(0)
    for name in tmp_namelist:
        lastname = p.get_initial(name).lower()
        final_namelist.append(lastname)

    final_name = ''.join(final_namelist)
    origin_email_address=final_name+'@your_email.com'
    return(origin_email_address)

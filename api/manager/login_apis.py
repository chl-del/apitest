# !/usr/bin python3
# encoding: utf-8 -*-
# @file     : login_apis.py
# @author   : 沙陌 Matongxue_2
# @Time     : 2023/7/27 20:23
# @Copyright: 北京码同学
from api.base_api import BaseManagerApi
from common.encry_decry import md5


class ManagerLoginApi(BaseManagerApi):

    # 接口的基本信息，统一封装在init函数中
    def __init__(self,username,password):
        super().__init__()
        self.url = f'{self.host}/admin/systems/admin-users/login'
        self.method = 'get'
        self.params = {
            "username":username,
            "password":md5(password),
            "captcha":'1512',
            "uuid":"asdasdasdasdasdd"
        }

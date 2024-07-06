# !/usr/bin python3
# encoding: utf-8 -*-
# @file     : goods_apis.py
# @author   : 沙陌 Matongxue_2
# @Time     : 2023/7/27 20:27
# @Copyright: 北京码同学
from api.base_api import BaseManagerApi


class GoodsBatchAuditApi(BaseManagerApi):

    def __init__(self,goods_ids:list):
        super().__init__()
        self.url = f'{self.host}/admin/goods/batch/audit'
        self.method = 'post'
        self.json = {
            "goods_ids": goods_ids,
            "message": "dsddd",
            "pass": 1
        }
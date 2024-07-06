# !/usr/bin python3
# encoding: utf-8 -*-
# @file     : conftest.py
# @author   : 沙陌 Matongxue_2
# @Time     : 2023/7/20 20:20
# @Copyright: 北京码同学
from typing import List

import pytest

from api.base_api import BaseBuyerApi, BaseSellerApi, BaseManagerApi
from api.buyer.checkout_params_apis import SetOrderAddressIdApi, SetOrderPayTypeApi
from api.buyer.login_apis import BuyerLoginApi
from api.buyer.member_address_apis import AddAddressApi
from api.manager.goods_apis import GoodsBatchAuditApi
from api.manager.login_apis import ManagerLoginApi
from api.seller.goods_apis import AddGoodsApi, GoodsUnderApi, GoodsRecycleApi, GoodsDeleteApi
from api.seller.login_apis import SellerLoginApi
from common.db_util import DBUtil
from common.logger import GetLogger
from common.redis_util import RedisUtil


def pytest_collection_modifyitems(config:"Config",items:List["Item"]):
    # items对象是pytest收集到的所有用例对象
    # 获取pytest.ini中的addopts值
    try:
        addopts = config.getini('addopts')
        if "--dist=each" in addopts:
            # 此时说明你要用的是多进程并发，我要得到当前的worker_id
            worker_id = config.workerinput.get('workerid')
        else:
            worker_id = None
    except:
        worker_id = None
    for item in items:
        # item就代表了一条用例
        if worker_id:
            item.originalname = item.originalname.encode('utf-8').decode("unicode-escape")+worker_id
            item._nodeid = item._nodeid.encode('utf-8').decode("unicode-escape")+worker_id
        else:
            item._nodeid = item._nodeid.encode('utf-8').decode("unicode-escape")


@pytest.fixture(scope='session',autouse=True)
def aalogger_init(worker_id):
    GetLogger.get_logger(worker_id).info('日志初始化成功')



@pytest.fixture(scope='session',autouse=True)
def buyer_login(worker_id):# 注意worker_id是pytest-xdist提供的
    # 实例化买家登录的接口类对象，完成调用，提取token，赋值给BaseBuyerApi.buyer_token
    # 没有使用多进程并发时，worker_id的值是master
    if worker_id=='gw0' or worker_id=='master':
        resp = BuyerLoginApi(username='shamo',password='shamo123').send()
    elif worker_id=='gw1':
        resp = BuyerLoginApi(username='shamo123', password='123456').send()
    BaseBuyerApi.buyer_token = resp.json()['access_token']
    BaseBuyerApi.uid = resp.json()['uid']

@pytest.fixture(scope='session',autouse=True)
def seller_login():
    # 实例化卖家登录的接口类对象，完成调用，提取token，赋值给BaseSellerApi.seller_token
    resp = SellerLoginApi(username='shamoseller',password='123456').send()
    BaseSellerApi.seller_token = resp.json()['access_token']
@pytest.fixture(scope='session',autouse=True)
def manager_login():
    # 实例化管理员登录的接口类对象，完成调用，提取token，赋值给BaseManagerApi.manager_token
    resp = ManagerLoginApi(username='admin',password='abc111').send()
    BaseManagerApi.manager_token = resp.json()['access_token']

@pytest.fixture(scope='session',autouse=False)
def redis_init():
    r = RedisUtil(host='82.156.74.26', port=6379, pwd='mtx')
    yield r

@pytest.fixture(scope='session',autouse=False)
def db_init():
    db_util = DBUtil(host='82.156.74.26',user='mtxshop_test',password='mtxshamo')
    yield db_util
    db_util.close()

@pytest.fixture(scope='class',autouse=False)
def goods_data(db_init):
    # 添加商品
    resp = AddGoodsApi().send()
    # 提取goods_id作为后续接口使用
    goods_id = resp.json()['goods_id']
    # 管理员审核商品
    GoodsBatchAuditApi(goods_ids=[goods_id]).send()
    # 审核完成后才会产生sku_id,我们重点就是要得到这个sku_id
    # 但是这个sku_id并不在审核接口的响应中
    # 我们需要从数据库中获取
    res = db_init.select(f'SELECT sku_id  FROM mtxshop_goods.es_goods_sku WHERE goods_id={goods_id}')
    sku_id = res[0]['sku_id']
    yield goods_id,sku_id
    # 后置处理，数据清除
    GoodsUnderApi(goods_ids=[goods_id]).send()
    GoodsRecycleApi(goods_ids=[goods_id]).send()
    GoodsDeleteApi(goods_ids=[goods_id]).send()

@pytest.fixture(scope='class',autouse=False)
def init_order_params(db_init):
    # 设置订单收货地址
    # 从数据库查询该买家用户名下的地址数据，如果数据库有数据，则从数据库拿到地址id，
    # 如果没有则调用新增收货地址的接口，从响应中拿到地址id，传递给设置订单收货地址接口
    res_list = db_init.select(f'SELECT * FROM  mtxshop_member.es_member_address ema WHERE member_id={BaseBuyerApi.uid}')
    if len(res_list)>0:# 说明数据库有数据
        address_id = res_list[0]['addr_id']
    else:
        # 调用新增收货地址接口
        resp = AddAddressApi().send()
        address_id = resp.json()['addr_id']
    SetOrderAddressIdApi(address_id=address_id).send()
    # 设置付款类型为货到付款
    SetOrderPayTypeApi().send()





























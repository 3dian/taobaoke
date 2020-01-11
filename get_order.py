#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/1/8 1:01 上午
# @Author  : Tang Jiuyang
# @Site    : https://tangjiuyang.com
# @File    : get_order_1min.py
# @Software: PyCharm
import requests
import configparser
import json
import pymysql
import sys
import datetime
import time
import os

base_dir = os.path.dirname(__file__)
# print(base_dir)
config = configparser.ConfigParser()
config.read("/root/www/taobaoke/config.ini")
ztkappkey = config['wechat']['ztkappkey']
mysql_pass = config['mysql']['password']
sid = config['wechat']['sid']


def get_orders(start_time, end_time, get_tk_status='0'):
    url = 'https://api.zhetaoke.com:10001/api/open_dingdanchaxun2.ashx'
    payload = dict()
    payload['appkey'] = ztkappkey
    payload['sid'] = sid
    payload['start_time'] = start_time
    payload['end_time'] = end_time
    payload['query_type'] = '2'
    payload['page_size'] = '100'
    payload['jump_type'] = '1'
    payload['page_no'] = '1'
    payload['order_scene'] = '1'
    payload['signurl'] = 1

    if get_tk_status != '0':
        payload['tk_status'] = get_tk_status
    next_page = True
    # 打开数据库连接
    db = pymysql.connect("127.0.0.1", "root", mysql_pass, "taobaoke")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    while next_page is True:
        top_url = requests.get(url, params=payload)
        top_url_json = json.loads(top_url.text)
        res = requests.get(top_url_json['url'])
        res_json = json.loads(res.text)
        data = res_json['tbk_sc_order_details_get_response']['data']
        next_page = data['has_next']
        get_one_page(data, cursor, db)
        payload['position_index'] = data['position_index']
        payload['page_no'] = str(int(payload['page_no']) + 1)
    db.close()


def get_one_page(data, cursor, db):
    results = data['results']
    try:
        results['publisher_order_dto']
    except KeyError:
        return
    for result in results['publisher_order_dto']:
        order_id = result['trade_parent_id']
        item_title = result['item_title']
        item_num = result['item_num']
        tb_paid_time = result['tb_paid_time']
        order_id_6 = order_id[-6:]
        pub_share_pre_fee = result['pub_share_pre_fee']
        total_commission_fee = result['total_commission_fee']
        tk_status = result['tk_status']
        # 查询订单是否存在
        update_sql = "UPDATE wechat_orders SET pub_share_pre_fee='%s', total_commission_fee='%s', tk_status='%s' WHERE order_id='%s'" % (
            pub_share_pre_fee, total_commission_fee, tk_status, order_id)
        insert_sql = "INSERT INTO wechat_orders(order_id, item_title, item_num, " \
                     "tb_paid_time, order_id_6, pub_share_pre_fee, total_commission_fee, " \
                     "tk_status) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                         order_id, item_title, item_num, tb_paid_time,
                         order_id_6,
                         pub_share_pre_fee,
                         total_commission_fee, tk_status)

        sql = 'select openid, alipay, name from wechat_orders where order_id_6=%s ' \
              'and alipay IS NOT NULL and name IS NOT NULL and openid IS NOT NULL;' % (
                  order_id_6)
        try:
            # 执行sql语句
            find_user_info_res = cursor.execute(sql)
            if find_user_info_res > 0:
                a = cursor.fetchone()
                openid, alipay, name = a
                insert_sql = "INSERT INTO wechat_orders(openid, order_id, item_title, item_num, " \
                             "tb_paid_time, order_id_6, pub_share_pre_fee, total_commission_fee, " \
                             "tk_status,alipay, name) VALUES('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s')" % (
                                 openid, order_id, item_title, item_num,
                                 tb_paid_time,
                                 order_id_6,
                                 pub_share_pre_fee,
                                 total_commission_fee, tk_status, alipay, name)
            update_res = cursor.execute(update_sql)
            if update_res > 0:
                # 执行sql语句
                db.commit()
            else:
                cursor.execute(insert_sql)
                db.commit()
        except Exception as e:
            print(e)
            # 发生错误时回滚
            db.rollback()


if __name__ == '__main__':
    # get_orders('2020-01-07 23:00:00', '2020-01-08 00:00:00')

    if sys.argv[1] == 'min':
        start_time = (datetime.datetime.now() - datetime.timedelta(
            minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        get_orders(start_time, end_time)
        print(datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),
              '订单查询成功!')
    if sys.argv[1] == 'day':
        start_time = (datetime.datetime.today() - datetime.timedelta(
            days=1)).strftime("%Y-%m-%d 00:00:00")
        for i in range(72):
            end_time = (datetime.datetime.strptime(start_time,
                                                   '%Y-%m-%d %H:%M:%S') - datetime.timedelta(
                minutes=-19)).strftime("%Y-%m-%d %H:%M:%S")
            get_orders(start_time, end_time)
            start_time = (datetime.datetime.strptime(end_time,
                                                     "%Y-%m-%d %H:%M:%S") - datetime.timedelta(
                minutes=-1)).strftime("%Y-%m-%d %H:%M:%S")
            time.sleep(10)
        print(datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),
              (datetime.datetime.today() - datetime.timedelta(days=1)).strftime(
                  "%Y-%m-%d"), '订单查询成功!')
    if sys.argv[1] == 'mon':
        start_time = (datetime.datetime.today() - datetime.timedelta(
            days=30)).strftime("%Y-%m-20 00:00:00")
        end_time = (datetime.datetime.strptime(start_time,
                                               '%Y-%m-%d %H:%M:%S') - datetime.timedelta(
            minutes=-19)).strftime("%Y-%m-%d %H:%M:%S")
        while end_time[:10] != datetime.datetime.today().strftime('%Y-%m-%d'):
            get_orders(start_time, end_time, get_tk_status='3')
            start_time = (datetime.datetime.strptime(end_time,
                                                     "%Y-%m-%d %H:%M:%S") - datetime.timedelta(
                minutes=-1)).strftime("%Y-%m-%d %H:%M:%S")
            end_time = (datetime.datetime.strptime(start_time,
                                                   '%Y-%m-%d %H:%M:%S') - datetime.timedelta(
                minutes=-19)).strftime("%Y-%m-%d %H:%M:%S")
            time.sleep(5)
        print(datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), (
                datetime.datetime.today() - datetime.timedelta(
            days=30)).strftime("%Y-%m"), '已结算订单查询成功!')

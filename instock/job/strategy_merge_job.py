#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import concurrent.futures
import pandas as pd
import os.path
import sys
import requests

cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)
import instock.lib.run_template as runt
import instock.core.tablestructure as tbs
import instock.lib.database as mdb
from instock.core.singleton_stock import stock_hist_data
from instock.core.stockfetch import fetch_stock_top_entity_data

__author__ = 'wyh'
__date__ = '2023/3/10 '

# 获取基本面选股的数据
def fetch_api_data(name: str, date: str):
    logging.info(f"fetch_api_data: {name}, {date}")
    """
    Fetch data from the API with given name and date.

    Args:
        name (str): The name parameter for the API.
        date (str): The date parameter for the API.

    Returns:
        Response: The response object from the API call.
    """
    url = "http://localhost:9988/instock/api_data"
    params = {
        "name": name,
        "date": date
    }
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'http://localhost:9988/instock/data?table_name=cn_stock_spot_buy',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    response = requests.get(url, headers=headers, params=params)
    return response

def repeat_stock_code(repeat_dict: dict, repeat_name_dict: dict, strategy_dict: dict, items: list, strategy_name: str):
    for k in items:
        code = k["code"]
        name = k["name"]
        if code in repeat_dict:
            repeat_dict[code] += 1
            if code in strategy_dict:
                strategy_dict[code].append(strategy_name)
        else:
            repeat_dict[code] = 1
            repeat_name_dict[code] = name
            strategy_dict[code] = [strategy_name]

def merge_strategy_data(date: str):
    # 使用字典记录出现次数和策略名称
    repeat_dict = {}
    repeat_name_dict = {}
    strategy_dict = {}  # 新增：记录每个股票出现在哪些策略中

    # 放量上涨数据
    cn_stock_strategy_enter = fetch_api_data("cn_stock_strategy_enter",date)
    repeat_stock_code(repeat_dict, repeat_name_dict, strategy_dict, cn_stock_strategy_enter.json(), "放量上涨")

    # 均线多头数据
    cn_stock_strategy_keep_increasing = fetch_api_data("cn_stock_strategy_keep_increasing",date)
    repeat_stock_code(repeat_dict, repeat_name_dict, strategy_dict, cn_stock_strategy_keep_increasing.json(), "均线多头")

    # 停机坪数据
    cn_stock_strategy_parking_apron = fetch_api_data("cn_stock_strategy_parking_apron",date)
    repeat_stock_code(repeat_dict, repeat_name_dict, strategy_dict, cn_stock_strategy_parking_apron.json(), "停机坪")

    # 回踩年线
    cn_stock_strategy_backtrace_ma250 = fetch_api_data("cn_stock_strategy_backtrace_ma250",date)
    repeat_stock_code(repeat_dict, repeat_name_dict, strategy_dict, cn_stock_strategy_backtrace_ma250.json(), "回踩年线")

    # 突破平台
    cn_stock_strategy_breakthrough_platform = fetch_api_data("cn_stock_strategy_breakthrough_platform",date)
    repeat_stock_code(repeat_dict, repeat_name_dict, strategy_dict, cn_stock_strategy_breakthrough_platform.json(), "突破平台")

    # 海龟交易法
    cn_stock_strategy_turtle_trade = fetch_api_data("cn_stock_strategy_turtle_trade",date)
    repeat_stock_code(repeat_dict, repeat_name_dict, strategy_dict, cn_stock_strategy_turtle_trade.json(), "海龟交易")

    # 高而窄的旗形
    cn_stock_strategy_high_tight_flag = fetch_api_data("cn_stock_strategy_high_tight_flag",date)
    repeat_stock_code(repeat_dict, repeat_name_dict, strategy_dict, cn_stock_strategy_high_tight_flag.json(), "高而窄的旗形")

    # 将repeat_dict按照出现次数排序
    repeat_dict = dict(sorted(repeat_dict.items(), key=lambda x: x[1], reverse=True))
    
    # 打印出现次数大于2的股票信息
    logging.info("\n=== 出现次数大于2的股票 ===")
    logging.info("代码  名称  出现次数  推荐策略")
    logging.info("-" * 50)
    for code, count in repeat_dict.items():
        if count >= 2:
            name = repeat_name_dict[code]
            strategies = ", ".join(strategy_dict[code])
            logging.info(f"{code}  {name}  {count}  {strategies}")

def main():
    runt.run_with_args(merge_strategy_data)


# main函数入口
if __name__ == '__main__':
    main()

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

def repeat_stock_code(repeat_dict: dict,repeat_name_dict:dict,  items: list):
    for k in items:
        code = k["code"]
        name = k["name"]
        if code in repeat_dict:
            repeat_dict[code] += 1
            repeat_name_dict[code] = name
        else:
            repeat_dict[code] = 1
            repeat_name_dict[code] = name


def merge_strategy_data(date: str):
    
    # 使用一个字典, 通过 code 记录分别在下面数据中出现的次数
    repeat_dict = {}
    repeat_name_dict = {}

    # 基本面选股数据
    #     [
    #     {
    #         "date": "/OADate(45615.0)/",
    #         "code": "301004",
    #         "name": "嘉益股份",
    #         "new_price": 104.73,
    #         "change_rate": 5.56,
    #         "ups_downs": 5.52,
    #         "volume": 9140,
    #         "deal_amount": 93561317,
    #         "amplitude": 5.58,
    #         "volume_ratio": 0.95,
    #         "turnoverrate": 1.01,
    #         "open_price": 99.34,
    #         "high_price": 104.75,
    #         "low_price": 99.21,
    #         "pre_close_price": 99.21,
    #         "speed_increase": 0.33,
    #         "speed_increase_5": 0.41,
    #         "speed_increase_60": 30.42,
    #         "speed_increase_all": 141.04,
    #         "dtsyl": 15.37,
    #         "pe9": 15.78,
    #         "pe": 23.05,
    #         "pbnewmrq": 6.48,
    #         "basic_eps": 5.11209,
    #         "bvps": 16.1702,
    #         "per_capital_reserve": 3.42832,
    #         "per_unassign_profit": 11.1995,
    #         "roe_weight": 35.92,
    #         "sale_gpr": 39.5439,
    #         "debt_asset_ratio": 26.274,
    #         "total_operate_income": 1985164070,
    #         "toi_yoy_ratio": 61.5969,
    #         "parent_netprofit": 530988792,
    #         "netprofit_yoy_ratio": 69.1999,
    #         "report_date": "/OADate(45565.0)/",
    #         "total_shares": 103869300,
    #         "free_shares": 95931463,
    #         "total_market_cap": 10878231789,
    #         "free_cap": 10046902120,
    #         "industry": "家用轻工",
    #         "listing_date": "/OADate(44372.0)/",
    #         "cdatetime": null
    #     }
    # ]
    # cn_stock_spot_buy = fetch_api_data("cn_stock_spot_buy",date)
    # repeat_stock_code(repeat_dict,repeat_name_dict, cn_stock_spot_buy.json())

    # names = [k["name"] for k in cn_stock_spot_buy.json()]
    # logging.info(f"names: {names}")

    # 放量上涨数据
    # [
    # {
    #     "date": "/OADate(45615.0)/",
    #     "code": "605577",
    #     "name": "\u9f99\u7248\u4f20\u5a92",
    # }
    # ]
    cn_stock_strategy_enter = fetch_api_data("cn_stock_strategy_enter",date)
    repeat_stock_code(repeat_dict,repeat_name_dict, cn_stock_strategy_enter.json())

    # # 均线多头数据
    # # 格式同上

    # cn_stock_strategy_keep_increasing = fetch_api_data("cn_stock_strategy_keep_increasing",date)
    # repeat_stock_code(repeat_dict,repeat_name_dict, cn_stock_strategy_keep_increasing.json())

    # # 停机坪数据
    # # 格式同上
    # cn_stock_strategy_parking_apron = fetch_api_data("cn_stock_strategy_parking_apron",date)
    # repeat_stock_code(repeat_dict,repeat_name_dict, cn_stock_strategy_parking_apron.json())

    # # 回踩年线
    # # 格式同上
    # cn_stock_strategy_backtrace_ma250 = fetch_api_data("cn_stock_strategy_backtrace_ma250",date)
    # repeat_stock_code(repeat_dict,repeat_name_dict, cn_stock_strategy_backtrace_ma250.json())

    # # 突破平台
    # # 格式同上
    # cn_stock_strategy_breakthrough_platform = fetch_api_data("cn_stock_strategy_breakthrough_platform",date)
    # repeat_stock_code(repeat_dict,repeat_name_dict, cn_stock_strategy_breakthrough_platform.json())

    # # 海龟交易法
    # # 格式同上
    # cn_stock_strategy_turtle_trade = fetch_api_data("cn_stock_strategy_turtle_trade",date)
    # repeat_stock_code(repeat_dict,repeat_name_dict, cn_stock_strategy_turtle_trade.json())

    # # 高而窄的旗形
    # # 格式同上
    # cn_stock_strategy_high_tight_flag = fetch_api_data("cn_stock_strategy_high_tight_flag",date)
    # repeat_stock_code(repeat_dict,repeat_name_dict, cn_stock_strategy_high_tight_flag.json())

    # 将repeat_dict按照出现次数排序
    repeat_dict = dict(sorted(repeat_dict.items(), key=lambda x: x[1], reverse=True))
    # 打印出code,name,和出现次数大于2的
    # for k,v in repeat_dict.items():
    #     if v > 2:
    #         logging.info(f"{k},{repeat_name_dict[k]},{v}")
    #按照出现次数降序打印
    for k,v in repeat_dict.items():
        logging.info(f"{k},{repeat_name_dict[k]},{v}")

def main():
    runt.run_with_args(merge_strategy_data)


# main函数入口
if __name__ == '__main__':
    main()

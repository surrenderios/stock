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


# 获取东方财富的评分
# curl 'https://datacenter-web.eastmoney.com/web/api/data/v1/get?reportName=RPT_CUSTOM_STOCK_PK&columns=ALL&filter=(SECURITY_CODE%3D%22002292%22)&client=WEB' \
#   -H 'Accept: */*' \
#   -H 'Accept-Language: en-US,en;q=0.9' \
#   -H 'Cache-Control: no-cache' \
#   -H 'Connection: keep-alive' \
#   -H 'Cookie: qgqp_b_id=1379118077646b8e9ea15fab58f3d8b2; websitepoptg_api_time=1735131770269; HAList=ty-0-002245-%u851A%u84DD%u9502%u82AF%2Cty-0-000981-%u5C71%u5B50%u9AD8%u79D1; st_si=58094261902913; emshistory=%5B%22%E6%98%93%E7%82%B9%E5%A4%A9%E4%B8%8B%22%2C%22%E4%BA%94%E6%B4%B2%E6%96%B0%E6%98%A5%22%2C%22%E6%AD%A3%E6%B5%B7%E7%A3%81%E6%9D%90%22%2C%22%E5%B4%87%E8%BE%BE%E6%8A%80%E6%9C%AF%22%2C%22%E6%96%B0%E9%87%8C%E7%A8%8B%22%2C%22%E9%BE%99%E6%97%97%E7%A7%91%E6%8A%80%22%2C%22%E5%8D%8E%E5%8B%A4%E6%8A%80%E6%9C%AF%22%2C%22%E5%8D%A7%E9%BE%99%E7%94%B5%E9%A9%B1%22%2C%22%E5%88%9B%E7%BB%B4%E6%95%B0%E5%AD%97%22%2C%22%E8%94%9A%E8%93%9D%E9%94%82%E8%8A%AF%22%5D; st_pvi=61600702723782; st_sp=2024-12-19%2019%3A57%3A45; st_inirUrl=https%3A%2F%2Fdata.eastmoney.com%2Fxuangu%2F; st_sn=23; st_psi=20241226210047783-118000300904-3226157163; st_asi=delete; JSESSIONID=221A64A572CD6AB61CEEA398F69A4CFA' \
#   -H 'Pragma: no-cache' \
#   -H 'Referer: https://so.eastmoney.com/web/s?keyword=%E6%98%93%E7%82%B9%E5%A4%A9%E4%B8%8B' \
#   -H 'Sec-Fetch-Dest: script' \
#   -H 'Sec-Fetch-Mode: no-cors' \
#   -H 'Sec-Fetch-Site: same-site' \
#   -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' \
#   -H 'sec-ch-ua: "Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"' \
#   -H 'sec-ch-ua-mobile: ?0' \
#   -H 'sec-ch-ua-platform: "macOS"'

def fetch_eastmoney_score(code: str):
    try:
        url = f"https://datacenter-web.eastmoney.com/web/api/data/v1/get?reportName=RPT_CUSTOM_STOCK_PK&columns=ALL&filter=(SECURITY_CODE%3D%22{code}%22)&client=WEB"
        response = requests.get(url)
        data = response.json()
        
        if not data.get("success") or not data.get("result") or not data["result"].get("data"):
            logging.warning(f"No valid data found for stock code: {code}")
            return None
            
        rise_probability = data["result"]["data"][0].get("RISE_1_PROBABILITY")
        if rise_probability is None:
            logging.warning(f"No rise probability found for stock code: {code}")
            return None
            
        return rise_probability
    except requests.RequestException as e:
        logging.error(f"Request failed for stock code {code}: {str(e)}")
        return None
    except (KeyError, IndexError, ValueError) as e:
        logging.error(f"Failed to parse data for stock code {code}: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error for stock code {code}: {str(e)}")
        return None


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
    logging.info("\n=== 出现次数2次以上的股票 ===")
    logging.info("代码  名称  出现次数  推荐策略  东方财富统计次日上涨概率")
    logging.info("-" * 50)
    for code, count in repeat_dict.items():
        if count >= 2:
            name = repeat_name_dict[code]
            strategies = ", ".join(strategy_dict[code])

            # 获取次日上涨概率
            rise_1_probability = fetch_eastmoney_score(code)
            rise_info = str(rise_1_probability) if rise_1_probability is not None else "N/A"
            logging.info(f"{code}  {name}  {count}  {strategies}  {rise_info}")

def main():
    runt.run_with_args(merge_strategy_data)


# main函数入口
if __name__ == '__main__':
    main()

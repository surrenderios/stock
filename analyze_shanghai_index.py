#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import requests
from datetime import datetime
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_sh_index_hist(start_date, end_date, index_code='000001'):
    """
    获取指数历史数据
    :param start_date: 开始日期
    :param end_date: 结束日期
    :param index_code: 指数代码
        000001: 上证指数
        000016: 上证50
        000300: 沪深300
        932000: 中证2000
    """
    try:
        # 确定市场代码
        market_code = '1' if index_code in ['000001', '000016'] else '1.' if index_code == '000300' else '2'
        secid = f"{market_code}.{index_code}"
        
        url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "ut": "7eea3edcaed734bea9cbfc24409ed989",
            "klt": "101",  # 日线
            "fqt": "1",
            "secid": secid,
            "beg": start_date,
            "end": end_date,
        }
        
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        
        if 'data' not in data or 'klines' not in data['data']:
            logging.error(f"No data returned from API for index {index_code}")
            return pd.DataFrame()
            
        # 解析数据
        records = []
        for line in data['data']['klines']:
            fields = line.split(',')
            records.append({
                'date': fields[0],
                'close': float(fields[2]),
                'change_pct': float(fields[8])
            })
            
        df = pd.DataFrame(records)
        df['date'] = pd.to_datetime(df['date'])
        return df
        
    except Exception as e:
        logging.error(f"Error fetching data for index {index_code}: {str(e)}")
        return pd.DataFrame()

def calculate_future_changes(df, high_change_dates):
    """
    计算大涨日后续的涨跌幅
    """
    future_changes = []
    
    for date in high_change_dates:
        date_idx = df[df['date'] == pd.to_datetime(date)].index[0]
        
        # 计算后1天涨跌幅
        next_1d_change = np.nan
        if date_idx + 1 < len(df):
            next_1d_change = df.iloc[date_idx + 1]['change_pct']
            
        # 计算后3天累计涨跌幅
        next_3d_change = np.nan
        if date_idx + 3 < len(df):
            next_3d_change = df.iloc[date_idx + 1:date_idx + 4]['change_pct'].sum()
            
        future_changes.append({
            'date': date,
            'change_pct': df.iloc[date_idx]['change_pct'],
            'next_1d_change': next_1d_change,
            'next_3d_change': next_3d_change
        })
    
    return pd.DataFrame(future_changes)

def get_high_change_dates(start_date, end_date, threshold=2.0):
    """
    获取指定时间段内上证指数涨幅超过阈值的日期（只统计上涨）及其后续表现
    :param start_date: 开始日期，格式：YYYYMMDD
    :param end_date: 结束日期，格式：YYYYMMDD
    :param threshold: 涨幅阈值，默认2.0%
    :return: DataFrame包含日期、涨幅及后续表现
    """
    # 获取上证指数数据
    df = fetch_sh_index_hist(start_date, end_date)
    
    if df.empty:
        logging.error("Failed to fetch Shanghai index data")
        return pd.DataFrame()
    
    # 筛选涨幅超过阈值的日期（只要上涨的）
    high_change_df = df[df['change_pct'] >= threshold].copy()
    
    # 按日期排序
    high_change_df = high_change_df.sort_values('date')
    high_change_dates = high_change_df['date'].dt.strftime('%Y-%m-%d').tolist()
    
    # 计算后续涨跌幅
    result_df = calculate_future_changes(df, high_change_dates)
    
    # 格式化列名
    result_df.columns = ['日期', '涨幅(%)', '次日涨跌幅(%)', '后3日累计涨跌幅(%)']
    
    return result_df

if __name__ == "__main__":
    # 示例：获取2023年至今涨幅超过2%的日期
    start_date = "20220101"
    end_date = datetime.now().strftime("%Y%m%d")
    
    result_df = get_high_change_dates(start_date, end_date)
    if not result_df.empty:
        print("\n上证指数涨幅超过2%的日期及后续表现：")
        print("-" * 70)
        pd.set_option('display.float_format', '{:.2f}'.format)
        print(result_df.to_string(index=False))
        
        # 统计后续表现
        print("\n统计分析：")
        print("-" * 70)
        print(f"大涨日次日上涨概率: {(result_df['次日涨跌幅(%)'] > 0).mean():.2%}")
        print(f"大涨日后3日上涨概率: {(result_df['后3日累计涨跌幅(%)'] > 0).mean():.2%}")
        print(f"次日平均涨跌幅: {result_df['次日涨跌幅(%)'].mean():.2f}%")
        print(f"后3日平均涨跌幅: {result_df['后3日累计涨跌幅(%)'].mean():.2f}%")
    else:
        print("未获取到数据或指定时间段内没有符合条件的数据") 
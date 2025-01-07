#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import requests
from datetime import datetime
import logging

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

def analyze_xmas_period():
    """
    分析2010-2023年间圣诞节前后各指数涨幅
    基准日：12.24（如果不是交易日则往后推到最近的交易日）
    结束日：12.28（如果不是交易日则往后推到最近的交易日）
    """
    # 定义要分析的指数
    indices = {
        '000001': '上证指数',
        '000016': '上证50',
        # '000300': '沪深300',
        '932000': '中证2000'
    }
    
    for index_code, index_name in indices.items():
        # 获取2010-2023年的数据
        df = fetch_sh_index_hist('20101201', '20240105', index_code)
        if df.empty:
            logging.error(f"Failed to fetch data for {index_name}")
            continue
            
        # 筛选12月24-31日的数据（扩大范围以处理节假日）
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['year'] = df['date'].dt.year
        
        xmas_data = df[
            (df['month'] == 12) & 
            (df['day'].between(27, 31))
        ]
        
        # 按年份计算涨幅
        yearly_stats = []
        for year in range(2010, 2024):
            year_data = xmas_data[xmas_data['year'] == year].copy()
            if not year_data.empty:
                try:
                    # 找到12.24后的第一个交易日（包括12.24）
                    base_data = year_data[year_data['day'] >= 24].sort_values('date').iloc[0]
                    base_date = base_data['date']
                    price_base = base_data['close']
                    
                    # 找到12.28后的第一个交易日（包括12.28）
                    end_data = year_data[year_data['day'] >= 28].sort_values('date').iloc[0]
                    end_date = end_data['date']
                    price_end = end_data['close']
                    
                    # 计算涨跌幅
                    change_pct = round((price_end - price_base) / price_base * 100, 2)
                    
                    yearly_stats.append({
                        'year': year,
                        'total_change_pct': change_pct,
                        'price_base': price_base,
                        'price_end': price_end,
                        'base_date': base_date.strftime('%Y-%m-%d'),
                        'end_date': end_date.strftime('%Y-%m-%d')
                    })
                except IndexError:
                    logging.warning(f"{year}年{index_name}数据不完整，跳过")
                    continue
        
        # 打印结果
        print(f"\n{index_name}圣诞节前后涨幅统计(2010-2023)：")
        print("-" * 110)
        print(f"{'年份':<6} {'基准日期':<12} {'基准收盘':<10} {'结束日期':<12} {'结束收盘':<10} {'涨跌幅%':<8}")
        print("-" * 110)
        
        for stat in yearly_stats:
            print(f"{stat['year']:<6} {stat['base_date']:<12} {stat['price_base']:<10.2f} "
                  f"{stat['end_date']:<12} {stat['price_end']:<10.2f} {stat['total_change_pct']:>6.2f}%")
        
        # 计算统计信息
        changes = [stat['total_change_pct'] for stat in yearly_stats]
        if changes:
            avg_change = sum(changes) / len(changes)
            positive_years = sum(1 for c in changes if c > 0)
            print("-" * 110)
            print(f"平均涨幅: {avg_change:.2f}%")
            print(f"上涨年数: {positive_years}/{len(changes)} ({positive_years/len(changes)*100:.1f}%)")
            
            # 计算最大涨幅和最大跌幅
            max_up = max(changes)
            max_down = min(changes)
            max_up_year = next(stat['year'] for stat in yearly_stats if stat['total_change_pct'] == max_up)
            max_down_year = next(stat['year'] for stat in yearly_stats if stat['total_change_pct'] == max_down)
            print(f"最大涨幅: {max_up:.2f}% ({max_up_year}年)")
            print(f"最大跌幅: {max_down:.2f}% ({max_down_year}年)")
        print("\n" + "=" * 110)  # 添加分隔线

if __name__ == "__main__":
    analyze_xmas_period() 
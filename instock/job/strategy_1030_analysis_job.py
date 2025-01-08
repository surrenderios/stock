#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import os.path
import sys
import json
from datetime import datetime, timedelta
import pandas as pd

cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)
import instock.lib.run_template as runt
from instock.core.singleton_stock import stock_data

__author__ = 'wyh'
__date__ = '2024/1/9'

def read_strategy_data(date: str) -> dict:
    """
    读取指定日期的策略推荐股票数据
    
    Args:
        date: 日期字符串，格式为 YYYY-MM-DD
        
    Returns:
        dict: 策略推荐的股票数据
    """
    strategy_file = os.path.join(cpath_current, "data", "strategy", date, "recommended_stocks.json")
    if not os.path.exists(strategy_file):
        logging.warning(f"No strategy data found for date {date}")
        return {}
        
    with open(strategy_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_performance_data(performance_data: dict, date: str) -> str:
    """
    将策略表现数据写入文件
    
    Args:
        performance_data: 策略表现数据
        date: 日期字符串，格式为 YYYY-MM-DD
        
    Returns:
        str: 写入文件的路径
    """
    strategy_dir = os.path.join(cpath_current, "data", "strategy", date)
    os.makedirs(strategy_dir, exist_ok=True)
    
    output_file = os.path.join(strategy_dir, "strategy_performance_1030.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(performance_data, f, ensure_ascii=False, indent=2)
    
    return output_file

def calculate_stock_performance(stock_info: dict, current_price: float, prev_date: str, current_date: str) -> dict:
    """
    计算单个股票的表现数据
    
    Args:
        stock_info: 股票的策略信息
        current_price: 当前价格
        prev_date: 前一个交易日
        current_date: 当前交易日
        
    Returns:
        dict: 股票的表现数据
    """
    prev_price = float(stock_info['price'])
    change = current_price - prev_price
    change_pct = (change / prev_price) * 100
    
    return {
        'code': stock_info['code'],
        'name': stock_info['name'],
        'strategies': stock_info['strategies'],
        'rise_probability': stock_info['rise_probability'],
        'prev_price': prev_price,
        'current_price': current_price,
        'price_change': round(change, 3),
        'change_pct': round(change_pct, 2),
        'prev_date': prev_date,
        'current_date': current_date,
        'current_time': '10:30'
    }

def analyze_strategy_performance(date):
    try:
        # 获取当前股票数据
        current_stocks = stock_data(date).get_data()
        if current_stocks is None or len(current_stocks.index) == 0:
            logging.warning(f"No stock data available for date {date}")
            return
            
        # 获取前一个交易日的日期
        prev_date = (date - timedelta(days=1)).strftime("%Y-%m-%d")
        current_date = date.strftime("%Y-%m-%d")
        
        # 读取前一天的策略推荐股票
        prev_stocks = read_strategy_data(prev_date)
        if not prev_stocks:
            return
            
        # 计算每只股票的表现
        performance = []
        for stock in prev_stocks:
            code = stock['code']
            if code in current_stocks.index:
                curr_price = float(current_stocks.loc[code]['close'])
                perf = calculate_stock_performance(stock, curr_price, prev_date, current_date)
                performance.append(perf)
        
        if not performance:
            logging.warning("No performance data to analyze")
            return
            
        # 转换为DataFrame进行统计分析
        df = pd.DataFrame(performance)
        
        # 计算汇总统计
        summary = {
            'average_return': round(df['change_pct'].mean(), 2),
            'win_rate': round(len(df[df['change_pct'] > 0]) / len(df) * 100, 2),
            'total_trades': len(df),
            'positive_trades': len(df[df['change_pct'] > 0]),
            'max_gain': round(df['change_pct'].max(), 2),
            'max_loss': round(df['change_pct'].min(), 2)
        }
        
        # 保存分析结果
        results = {
            'summary': summary,
            'trades': performance
        }
        
        output_file = write_performance_data(results, current_date)
        
        # 输出汇总信息
        logging.info("\n=== 策略表现分析（10:30） ===")
        logging.info(f"平均收益率: {summary['average_return']}%")
        logging.info(f"胜率: {summary['win_rate']}%")
        logging.info(f"总交易数: {summary['total_trades']}")
        logging.info(f"盈利交易数: {summary['positive_trades']}")
        logging.info(f"最大收益: {summary['max_gain']}%")
        logging.info(f"最大回撤: {summary['max_loss']}%")
        logging.info(f"\n详细分析结果已保存至: {output_file}")
            
    except Exception as e:
        logging.error(f"Error in analyze_strategy_performance: {str(e)}")

def main():
    runt.run_with_args(analyze_strategy_performance)

# main函数入口
if __name__ == '__main__':
    main() 
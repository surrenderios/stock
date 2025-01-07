#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import yfinance as yf
import talib

# 1. 数据获取
def get_stock_data(ticker, start_date, end_date):
    """
    获取股票历史数据
    """
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

# 2. 指标计算
def calculate_technical_indicators(data):
    """
    计算技术指标：均线、MACD、RSI
    """
    # 计算均线
    data['MA_5'] = talib.SMA(data['Close'], timeperiod=5)
    data['MA_10'] = talib.SMA(data['Close'], timeperiod=10)
    
    # 计算MACD
    data['MACD'], data['MACD_signal'], _ = talib.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    
    # 计算RSI
    data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
    
    return data

# 3. 筛选股票
def filter_stocks(data):
    """
    筛选符合趋势的股票
    """
    # 筛选条件
    condition = (
        (data['MA_5'] > data['MA_10']) &  # 5日均线 > 10日均线
        (data['MACD'] > data['MACD_signal']) &  # MACD金叉
        (data['RSI'] < 70)  # RSI未超买
    )
    filtered_data = data[condition]
    return filtered_data

# 4. 回测验证
def backtest_strategy(filtered_data, initial_capital=100000):
    """
    回测策略
    """
    # 假设每次买入等金额的股票
    num_stocks = len(filtered_data)
    capital_per_stock = initial_capital / num_stocks
    
    # 计算收益率
    filtered_data['Return'] = filtered_data['Close'].pct_change()
    filtered_data['Cumulative_Return'] = (1 + filtered_data['Return']).cumprod()
    
    # 计算总收益
    total_return = (filtered_data['Cumulative_Return'].iloc[-1] - 1) * 100
    print(f"策略总收益率: {total_return:.2f}%")

# 主函数
def main():
    # 参数设置
    tickers = ['601318' ]  # 股票列表
    start_date = '2024-12-01'
    end_date = '2024-12-27'
    initial_capital = 100000  # 初始资金

    # 遍历股票
    for ticker in tickers:
        print(f"分析股票: {ticker}")
        # 获取数据
        data = get_stock_data(ticker, start_date, end_date)
        # 计算技术指标
        data = calculate_technical_indicators(data)
        # 筛选股票
        filtered_data = filter_stocks(data)
        # 回测策略
        if not filtered_data.empty:
            backtest_strategy(filtered_data, initial_capital)
        else:
            print("无符合筛选条件的股票")

if __name__ == "__main__":
    main()
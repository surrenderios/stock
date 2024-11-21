#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import datetime
import concurrent.futures
import logging
import os.path
import sys

# 在项目运行时，临时将项目路径添加到环境变量
cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)
log_path = os.path.join(cpath_current, 'log')
if not os.path.exists(log_path):
    os.makedirs(log_path)
logging.basicConfig(format='%(asctime)s %(message)s', filename=os.path.join(log_path, 'stock_execute_job.log'))
logging.getLogger().setLevel(logging.INFO)
import init_job as bj
import basic_data_daily_job as hdj
import basic_data_other_daily_job as hdtj
import basic_data_after_close_daily_job as acdj
import indicators_data_daily_job as gdj
import strategy_data_daily_job as sdj
import backtest_data_daily_job as bdj
import klinepattern_data_daily_job as kdj
import selection_data_daily_job as sddj
import strategy_merge_job as mergejb

__author__ = 'myh '
__date__ = '2023/3/10 '

def print_step_info(step_name, start_time):
    """打印每一步的耗时信息"""
    elapsed = time.time() - start_time
    logging.info(f"完成{step_name}, 耗时: {elapsed:.2f} 秒")

def main():
    start = time.time()
    _start = datetime.datetime.now()
    logging.info("######## 任务执行时间: %s #######" % _start.strftime("%Y-%m-%d %H:%M:%S.%f"))

    # 第1步：初始化数据库
    step_start = time.time()
    logging.info("######## 开始第1步：初始化数据库 #######")
    bj.main()
    print_step_info("第1步：初始化数据库", step_start)

    # 第2.1步：创建股票基础数据表
    step_start = time.time()
    logging.info("######## 开始第2.1步：创建股票基础数据表 #######")
    hdj.main()
    print_step_info("第2.1步：创建股票基础数据表", step_start)

    # 第2.2步：创建综合股票数据表
    step_start = time.time()
    logging.info("######## 开始第2.2步：创建综合股票数据表 #######")
    sddj.main()
    print_step_info("第2.2步：创建综合股票数据表", step_start)

    # 并行执行第3.1、3.2、4、5步
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 第3.1步：创建股票其它基础数据表
        step_start_3_1 = time.time()
        logging.info("######## 开始第3.1步：创建股票其它基础数据表 #######")
        future_3_1 = executor.submit(hdtj.main)

        # 第3.2步：创建股票指标数据表
        step_start_3_2 = time.time()
        logging.info("######## 开始第3.2步：创建股票指标数据表 #######")
        future_3_2 = executor.submit(gdj.main)

        # 第4步：创建股票k线形态表
        # step_start_4 = time.time()
        # logging.info("######## 开始第4步：创建股票k线形态表 #######")
        # future_4 = executor.submit(kdj.main)

        # 第5步：创建股票策略数据表
        step_start_5 = time.time()
        logging.info("######## 开始第5步：创建股票策略数据表 #######")
        future_5 = executor.submit(sdj.main)

        # 等待所有任务完成并打印耗时
        future_3_1.result()
        print_step_info("第3.1步：创建股票其它基础数据表", step_start_3_1)
        
        future_3_2.result()
        print_step_info("第3.2步：创建股票指标数据表", step_start_3_2)
        
        # future_4.result()
        # print_step_info("第4步：创建股票k线形态表", step_start_4)
        
        future_5.result()
        print_step_info("第5步：创建股票策略数据表", step_start_5)

    # 合并筛选
    step_start = time.time()
    logging.info("######## 开始合并筛选步骤 #######")
    mergejb.main()
    print_step_info("合并筛选步骤", step_start)

    # 第6步：创建股票回测
    step_start = time.time()
    logging.info("######## 开始第6步：创建股票回测 #######")
    bdj.main()
    print_step_info("第6步：创建股票回测", step_start)

    # 第7步：创建股票闭盘后才有的数据
    step_start = time.time()
    logging.info("######## 开始第7步：创建股票闭盘后才有的数据 #######")
    acdj.main()
    print_step_info("第7步：创建股票闭盘后才有的数据", step_start)

    logging.info("######## 完成所有任务, 总耗时: %.2f 秒 #######" % (time.time() - start))

# main函数入口
if __name__ == '__main__':
    main()

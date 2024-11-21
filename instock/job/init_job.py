#!/usr/local/bin/python3
# -*- coding: utf-8 -*-


import logging
import pymysql
import os.path
import sys

cpath_current = os.path.dirname(os.path.dirname(__file__))
cpath = os.path.abspath(os.path.join(cpath_current, os.pardir))
sys.path.append(cpath)
import instock.lib.database as mdb

__author__ = 'myh '
__date__ = '2023/3/10 '


# 创建新数据库。
def create_new_database():
    _MYSQL_CONN_DBAPI = mdb.MYSQL_CONN_DBAPI.copy()
    _MYSQL_CONN_DBAPI['database'] = "mysql"
    with pymysql.connect(**_MYSQL_CONN_DBAPI) as conn:
        with conn.cursor() as db:
            try:
                create_sql = f"CREATE DATABASE IF NOT EXISTS `{mdb.db_database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
                db.execute(create_sql)
                create_new_base_table()
            except Exception as e:
                logging.error(f"init_job.create_new_database处理异常：{e}")


# 创建基础表。
def create_new_base_table():
    with pymysql.connect(**mdb.MYSQL_CONN_DBAPI) as conn:
        with conn.cursor() as db:
            create_table_sql = """CREATE TABLE IF NOT EXISTS `cn_stock_attention` (
                                  `datetime` datetime(0) NULL DEFAULT NULL, 
                                  `code` varchar(6) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
                                  PRIMARY KEY (`code`) USING BTREE,
                                  INDEX `INIX_DATETIME`(`datetime`) USING BTREE
                                  ) CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;"""
            db.execute(create_table_sql)
            
            # Add new initialization tracking table
            init_table_sql = """CREATE TABLE IF NOT EXISTS `system_init_status` (
                              `key` varchar(50) NOT NULL,
                              `status` tinyint(1) NOT NULL DEFAULT 0,
                              `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                              PRIMARY KEY (`key`)
                              ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;"""
            db.execute(init_table_sql)


def check_database():
    with pymysql.connect(**mdb.MYSQL_CONN_DBAPI) as conn:
        with conn.cursor() as db:
            db.execute(" select 1 ")


# ALERT table中的 utf8mb3_uca1400_ai_ci为 utf8mb3_general_ci
def alert_table():
    with pymysql.connect(**mdb.MYSQL_CONN_DBAPI) as conn:
        with conn.cursor() as db:
            # Check if already executed
            db.execute("SELECT status FROM system_init_status WHERE `key` = 'alert_table_executed'")
            result = db.fetchone()
            
            if result and result[0] == 1:
                logging.info("alert_table已经执行过，跳过执行")
                return
                
            # Execute all ALTER statements
            alert_sql = [
                "ALTER TABLE `cn_stock_spot` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_spot` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_spot` MODIFY COLUMN `industry` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_etf_spot` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_etf_spot` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_selection` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_selection` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_selection` MODIFY COLUMN `industry` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_selection` MODIFY COLUMN `area` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_selection` MODIFY COLUMN `concept` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_selection` MODIFY COLUMN `style` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_selection` MODIFY COLUMN `is_hs300` varchar(2) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_selection` MODIFY COLUMN `is_sz50` varchar(2) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_selection` MODIFY COLUMN `is_zz500` varchar(2) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_selection` MODIFY COLUMN `is_zz1000` varchar(2) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_selection` MODIFY COLUMN `is_cy50` varchar(2) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_selection` MODIFY COLUMN `predict_type` varchar(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_selection` MODIFY COLUMN `org_rating` varchar(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_selection` MODIFY COLUMN `secucode` varchar(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_top` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_top` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_spot_buy` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_spot_buy` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_spot_buy` MODIFY COLUMN `industry` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_bonus` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_bonus` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_bonus` MODIFY COLUMN `progress` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_fund_flow` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_fund_flow` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_fund_flow_industry` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_fund_flow_industry` MODIFY COLUMN `stock_name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_fund_flow_industry` MODIFY COLUMN `stock_name_5` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_fund_flow_industry` MODIFY COLUMN `stock_name_10` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_fund_flow_concept` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_fund_flow_concept` MODIFY COLUMN `stock_name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_fund_flow_concept` MODIFY COLUMN `stock_name_5` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_fund_flow_concept` MODIFY COLUMN `stock_name_10` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_strategy_keep_increasing` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_strategy_keep_increasing` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_strategy_backtrace_ma250` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_strategy_backtrace_ma250` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_strategy_breakthrough_platform` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_strategy_breakthrough_platform` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_strategy_turtle_trade` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_strategy_turtle_trade` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_strategy_parking_apron` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_strategy_parking_apron` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_pattern` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_pattern` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_strategy_enter` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_strategy_enter` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_indicators` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_indicators` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_indicators_buy` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_indicators_buy` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_strategy_high_tight_flag` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_strategy_high_tight_flag` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_blocktrade` MODIFY COLUMN `code` varchar(6) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
                "ALTER TABLE `cn_stock_blocktrade` MODIFY COLUMN `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci",
            ]
            
            for sql in alert_sql:
                logging.info(f"exec:{sql}")
                db.execute(sql)
            
            # Mark as executed
            db.execute("""INSERT INTO system_init_status (`key`, status) 
                         VALUES ('alert_table_executed', 1)
                         ON DUPLICATE KEY UPDATE status = 1""")
            conn.commit()

def main():
    # 检查，如果执行 select 1 失败，说明数据库不存在，然后创建一个新的数据库。
    try:
        check_database()
    except Exception as e:
        logging.error("执行信息：数据库不存在，将创建。")
        # 检查数据库失败，
        create_new_database()
    # 修复表结构
    alert_table()


# main函数入口
if __name__ == '__main__':
    main()

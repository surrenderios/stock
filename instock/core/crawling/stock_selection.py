# -*- coding:utf-8 -*-
# !/usr/bin/env python

import pandas as pd
import requests
import instock.core.tablestructure as tbs
import logging

__author__ = 'myh '
__date__ = '2023/5/9 '


def stock_selection() -> pd.DataFrame:
    """
    东方财富网-个股-选股器
    https://data.eastmoney.com/xuangu/
    :return: 选股器
    :rtype: pandas.DataFrame
    """
    try:
        cols = tbs.TABLE_CN_STOCK_SELECTION['columns']
        sty = ""  # 初始值 "SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,CHANGE_RATE"
        for k in cols:
            sty = f"{sty},{cols[k]['map']}"
        url = "https://data.eastmoney.com/dataapi/xuangu/list"
        params = {
            "sty": sty[1:],
            # "filter": "(MARKET+in+(\"上交所主板\",\"深交所主板\",\"深交所创业板\"))(NEW_PRICE>0)",
            "filter": "(MARKET+in+(\"上交所主板\",\"深交所主板\"))(NEW_PRICE>0)",
            "p": 1,
            "ps": 2000,
            "source": "SELECT_SECURITIES",
            "client": "WEB"
        }
        
        r = requests.get(url, params=params)
        
        # Check if request was successful
        r.raise_for_status()
        
        # Log response details for debugging
        logging.debug(f"API Response Status Code: {r.status_code}")
        logging.debug(f"API Response Headers: {r.headers}")
        logging.debug(f"API Response Content: {r.text[:1000]}")  # Log first 1000 chars to avoid huge logs
        
        # Try to parse JSON response
        data_json = r.json()
        
        if not isinstance(data_json, dict):
            logging.error(f"Unexpected response format. Expected dict, got {type(data_json)}")
            return pd.DataFrame()
            
        if "result" not in data_json:
            logging.error(f"Response missing 'result' key. Keys found: {data_json.keys()}")
            return pd.DataFrame()
            
        if "data" not in data_json["result"]:
            logging.error(f"Result missing 'data' key. Keys found: {data_json['result'].keys()}")
            return pd.DataFrame()
            
        data = data_json["result"]["data"]
        if not data:
            logging.info("No data returned from API")
            return pd.DataFrame()
            
        temp_df = pd.DataFrame(data)

        # Handle CONCEPT and STYLE columns if they exist
        if 'CONCEPT' in temp_df.columns:
            mask = ~temp_df['CONCEPT'].isna()
            temp_df.loc[mask, 'CONCEPT'] = temp_df.loc[mask, 'CONCEPT'].apply(lambda x: ', '.join(x) if isinstance(x, (list, tuple)) else x)
        
        if 'STYLE' in temp_df.columns:
            mask = ~temp_df['STYLE'].isna()
            temp_df.loc[mask, 'STYLE'] = temp_df.loc[mask, 'STYLE'].apply(lambda x: ', '.join(x) if isinstance(x, (list, tuple)) else x)

        for k in cols:
            if cols[k]["map"] not in temp_df.columns:
                logging.warning(f"Column {cols[k]['map']} not found in API response")
                continue
                
            t = tbs.get_field_type_name(cols[k]["type"])
            if t == 'numeric':
                temp_df[cols[k]["map"]] = pd.to_numeric(temp_df[cols[k]["map"]], errors="coerce")
            elif t == 'datetime':
                temp_df[cols[k]["map"]] = pd.to_datetime(temp_df[cols[k]["map"]], errors="coerce").dt.date

        return temp_df
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {str(e)}")
        return pd.DataFrame()
    except ValueError as e:
        logging.error(f"JSON parsing failed: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"Unexpected error in stock_selection: {str(e)}")
        return pd.DataFrame()


def stock_selection_params():
    """
    东方财富网-个股-选股器-选股指标
    https://data.eastmoney.com/xuangu/
    :return: 选股器-选股指标
    :rtype: pandas.DataFrame
    """
    url = "https://datacenter-web.eastmoney.com/wstock/selection/api/data/get"
    params = {
        "type": "RPTA_PCNEW_WHOLE",
        "sty": "ALL",
        "p": 1,
        "ps": 50000,
        "source": "SELECT_SECURITIES",
        "client": "WEB"
    }

    r = requests.get(url, params=params)
    data_json = r.json()
    zxzb = data_json["zxzb"]  # 指标
    print(zxzb)


if __name__ == "__main__":
    stock_selection_df = stock_selection()
    print(stock_selection)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

def fetch_eastmoney_score(code: str):
    url = f"https://datacenter-web.eastmoney.com/web/api/data/v1/get?reportName=RPT_CUSTOM_STOCK_PK&columns=ALL&filter=(SECURITY_CODE%3D%22{code}%22)&client=WEB"
    response = requests.get(url)
    return response.json()

if __name__ == "__main__":
    print(fetch_eastmoney_score("002292"))
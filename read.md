
# 配置

sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11

# 安装 Python 3.11 的 distutils 模块
sudo apt install python3.11-distutils

# 安装 ensurepip 所需的工具
sudo apt install python3.11-venv

python3.11 -m venv myenv
source myenv/bin/activate

# 系统
ubuntu 22.04


## 安装db
sudo docker run -d --name InStockDbService \
-v /data/mariadb/data:/var/lib/instockdb \
-e MYSQL_ROOT_PASSWORD=root \
library/mariadb:latest

## 编译stock镜像
1. git clone https://github.com/surrenderios/stock.git
2. cd stock/docker
3. ./build.sh


## 运行stock
1. docker run -dit --name InStock --link=InStockDbService \
-p 9988:9988 \
-e db_host=InStockDbService \
mayanghua/instock:202412

## 查看日志
1. docker exec -it InStock /bin/bash
2. tail -f InStock/instock/log/stock_execute_job.log


## 重新编译stock以后运行
1. docker ps -a && docker stop InStock && docker rm InStock

2. docker run -dit --name InStock --link=InStockDbService \
-p 9988:9988 \
-e db_host=InStockDbService \
mayanghua/instock:202501



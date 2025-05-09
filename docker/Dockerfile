# 基础镜像
FROM centos:7

MAINTAINER myh
#增加语言utf-8
ENV LANG=zh_CN.UTF-8
ENV LC_CTYPE=zh_CN.UTF-8
ENV LC_ALL=C
ENV PYTHONPATH=/data/InStock
EXPOSE 9988

# 使用国内镜像地址加速。修改yum源，pip地址，设置时区
RUN yum install -y epel-release && \
    yum install -y python3 python3-pip python3-devel gcc make mysql-devel pkgconfig curl cronie && \
    echo  "[global]\n\
index-url = https://mirrors.aliyun.com/pypi/simple\n\
trusted-host = mirrors.aliyun.com" > /etc/pip.conf && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    pip3 install supervisor && \
    pip3 install mysqlclient && \
    pip3 install requests && \
    pip3 install arrow && \
    pip3 install numpy && \
    pip3 install SQLAlchemy && \
    pip3 install PyMySQL && \
    pip3 install Logbook && \
    pip3 install python_dateutil && \
    pip3 install py_mini_racer && \
    pip3 install tqdm && \
    pip3 install beautifulsoup4 && \
    pip3 install bokeh && \
    pip3 install pandas && \
    pip3 install tornado && \
    pip3 install easytrader && \
    curl -SL https://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz | tar -xzC . && \
    cd ta-lib/  && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    pip3 install TA-Lib && \
    rm -rf ta-lib* && \
    yum remove -y gcc make python3-devel mysql-devel curl && \
    yum clean all && \
    rm -rf /var/cache/yum/* && \
    rm -rf /root/.cache/*

WORKDIR /data
#InStock软件
COPY stock /data/InStock
COPY cron/cron.hourly /etc/cron.hourly
COPY cron/cron.workdayly /etc/cron.workdayly
COPY cron/cron.monthly /etc/cron.monthly
COPY cron/cron.work1430 /etc/cron.work1430
COPY cron/cron.work1030 /etc/cron.work1030

#add cron sesrvice.
#任务调度
RUN chmod 755 /data/InStock/instock/bin/run_*.sh && \
    chmod 755 /etc/cron.hourly/* && chmod 755 /etc/cron.workdayly/* && chmod 755 /etc/cron.monthly/* && chmod 755 /etc/cron.work1430/* && chmod 755 /etc/cron.work1030/* && \
    echo "SHELL=/bin/sh \n\
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin \n\
# min hour day month weekday command \n\
*/30 9,10,11,13,14,15 * * 1-5 /bin/run-parts /etc/cron.hourly \n\
30 17 * * 1-5 /bin/run-parts /etc/cron.workdayly \n\
30 14 * * 1-5 /bin/run-parts /etc/cron.work1430 \n\
30 10 * * 1-5 /bin/run-parts /etc/cron.work1030 \n\
30 10 * * 3,6 /bin/run-parts /etc/cron.monthly \n" > /var/spool/cron/crontabs/root && \
    chmod 600 /var/spool/cron/crontabs/root

ENTRYPOINT ["supervisord","-n","-c","/data/InStock/supervisor/supervisord.conf"]
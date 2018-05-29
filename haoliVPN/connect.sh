#!/bin/bash

basepath=$(cd `dirname $0`; pwd)

cd $basepath

if [ -f $basepath/connect-log.log ];then
    ./connect.py connect $common_name $trusted_ip $trusted_port $ifconfig_pool_remote_ip >>$basepath/connect-log.log
else
    touch $basepath/connect-log.log
    ./connect.py connect $common_name $trusted_ip $trusted_port $ifconfig_pool_remote_ip >>$basepath/connect-log.log
fi

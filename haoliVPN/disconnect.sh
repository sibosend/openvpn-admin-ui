#!/bin/bash

basepath=$(cd `dirname $0`; pwd)

cd $basepath

if [ -f $basepath/connect-log.log ];then
    ./connect.py disconnect $common_name $bytes_received $bytes_sent >>$basepath/connect-log.log
else
    touch $basepath/connect-log.log
    ./connect.py disconnect $common_name $bytes_received $bytes_sent >>$basepath/connect-log.log
fi


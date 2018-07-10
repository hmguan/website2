#!/bin/bash

while [ true ]
do 

	date_today=`date "+%Y%m%d"`
	date_today_format=`date "+%Y%m%d_%H%M%S"`
	date_yes=`date -d '1 days ago' +%Y%m%d`
	date_before_2=`date -d '2 days ago' +%Y%m%d`
	date_before_3=`date -d '3 days ago' +%Y%m%d`
	date_before_4=`date -d '4 days ago' +%Y%m%d`
	date_before_5=`date -d '5 days ago' +%Y%m%d`
	mkdir -p /gzrobot/log/
	echo $date_today >>/gzrobot/log/"delete_file_"$date_today_format".log"

	######### delete business log #################
	find /gzrobot/log/ -type f | grep -v '.log'  >>/gzrobot/log/"delete_file_"$date_today_format".log"
	find /gzrobot/log/ -type f | grep -v '.log' | xargs rm -f
	find /gzrobot/log/ -type f | grep -v $date_today |grep -v $date_yes |grep -v $date_before_2  >>/gzrobot/log/"delete_file_"$date_today_format".log"
	find /gzrobot/log/ -type f | grep -v $date_today |grep -v $date_yes |grep -v $date_before_2 | xargs rm -f 
	find /agvshell/log/ -type f | grep -v '.log' >>/gzrobot/log/"delete_file_"$date_today_format".log"
	find /agvshell/log/ -type f | grep -v '.log' | xargs rm -f
	find /agvshell/log/ -type f | grep -v $date_today |grep -v $date_yes |grep -v $date_before_2 >>/gzrobot/log/"delete_file_"$date_today_format".log"
	find /agvshell/log/ -type f | grep -v $date_today |grep -v $date_yes |grep -v $date_before_2 | xargs rm -f 

	######### gzip today and yesterday's log files #################
	find /gzrobot/log/ -type f -name '*.log' | grep -v $date_today | xargs gzip
	find /agvshell/log/ -type f -name '*.log' | grep -v $date_today | xargs gzip

	######### delete system log #################
	find /var/log/ -type f -name '*messages*' -size +300M >>/gzrobot/log/"delete_file_"$date_today_format".log"
	find /var/log/ -type f -name '*messages*' -size +300M -exec sh -c 'cat /dev/null> {}' \;
	find /var/log/ -type f -name '*syslog*' -size +300M >>/gzrobot/log/"delete_file_"$date_today_format".log"
	find /var/log/ -type f -name '*syslog*' -size +300M -exec sh -c 'cat /dev/null> {}' \;
	find /var/log/ -type f -name '*daemon*' -size +300M >>/gzrobot/log/"delete_file_"$date_today_format".log"
	find /var/log/ -type f -name '*daemon*' -size +300M -exec sh -c 'cat /dev/null> {}' \;
	find /var/log/ -type f -name '*.gz' |xargs rm -rf
	
	sleep 3600
	
done;

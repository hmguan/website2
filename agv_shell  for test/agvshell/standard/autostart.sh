#!/bin/bash
#
# created by guanlinbo@gzrobot.com
# 2017-08-26
#


date -s "2016-01-01 15:00:00"
date_today=`date "+%Y%m%d"`
loop_i=0

#prepare work, you may change these variables to more reasonable values
ip_ntp_server=192.168.1.27
if [ $# -gt 0 ]; then
	ip_ntp_server=$1
fi
ip_ac=192.168.0.1

#step 1 -------------------------------------------------
##create directory and softlink 
if [ ! -d "/agvshell/standard" ]; then
    mkdir -p /agvshell/standard/
fi
chmod +rw /agvshell/standard

if [ ! -d "/agvshell/standard/gzrobot" ]; then
    ln -sf /gzrobot /agvshell/standard/gzrobot
fi

if [ ! -d "/agvshell/standard/agv" ]; then
    ln -sf /etc/agv /agvshell/standard/agv
fi

if [ ! -d "/agvshell/standard/lib" ]; then
    mkdir /agvshell/standard/lib
fi

if [ -d "/usr/local/lib64" ]; then
    ln -sf /usr/local/lib64/libgzcamera.so /agvshell/standard/lib/libgzcamera.so
    ln -sf /usr/local/lib64/libjpeg.so.62 /agvshell/standard/lib/libjpeg.so.62
    ln -sf /usr/local/lib64/motion_net.so /agvshell/standard/lib/motion_net.so
    ln -sf /usr/local/lib64/nshost.so /agvshell/standard/lib/nshost.so
else
    ln -sf /usr/local/lib/libgzcamera.so /agvshell/standard/lib/libgzcamera.so
    ln -sf /usr/local/lib/libjpeg.so.62 /agvshell/standard/lib/libjpeg.so.62
    ln -sf /usr/local/lib/motion_net.so /agvshell/standard/lib/motion_net.so
    ln -sf /usr/local/lib/nshost.so /agvshell/standard/lib/nshost.so
fi

#step 2 ---------------------------------------------------
#sleep 1
mkdir -p /gzrobot/log/
echo "start to connect ac..." >>/gzrobot/log/$date_today"_start.log"
while [ true ]
do 
    sleep 1
	ping -c 1 -w 1 $ip_ac > /dev/null
	if [ $? -eq 0 ];then
		break
	fi
	loop_i=$[loop_i+1]
	if [ $loop_i -eq 5 ]; then
		echo "ac not connected" >>/gzrobot/log/$date_today"_start.log"
		loop_i=0
	fi
done
echo "ac connected" >>/gzrobot/log/$date_today"_start.log"


#step3 ---------------------------------------------------
loop_i=0
while [ true ]
do 
	/usr/bin/pkill -9 ntpd
	sleep 2
	/usr/sbin/ntpdate -t 2 -p 1 $ip_ntp_server 
	cur_date=`date "+%Y%m%d"`
	if [ $cur_date -gt 20160101 ];then
	  break
	fi
	loop_i=$[loop_i+1]
	if [ $loop_i -eq 5 ]; then
		echo "ntp server not ready" >>/gzrobot/log/$date_today"_start.log"
		loop_i=0
	fi
done
echo "ntp server started" >>/gzrobot/log/$date_today"_start.log"
sleep 3


#step 4 ---------------------------------------------------
/usr/sbin/ntpd -p /var/run/ntpd.pid -g -u 112:116 &
#waiting for M core to synchronize
sleep 20


#step 5 ---------------------------------------------------
### delete log
sleep 0.5
if [ -f "/gzrobot/clear_log.sh" ]; then
    /bin/chmod +x /gzrobot/clear_log.sh
    cd /gzrobot/
    /gzrobot/clear_log.sh &
fi

#step 6 ---------------------------------------------------
### ping ip tables
sleep 0.5
if [ -f "/gzrobot/ping_ips.sh" ]; then
    /bin/chmod +x /gzrobot/ping_ips.sh
    cd /gzrobot/
    /gzrobot/ping_ips.sh &
fi


#exit 0

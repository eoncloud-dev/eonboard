#!/bin/sh

CURRENT_USER=`whoami`
echo $CURRENT_USER
if [ "$CURRENT_USER" = "eoncloud" ]; then
	cd /var/www/eoncloud_web/eoncloud_web/
	../.venv/bin/celery multi start eoncloud_worker -A cloud --pidfile=/var/log/eoncloud/celery_%n.pid --logfile=/var/log/eoncloud/celery_%n.log
	sleep 3
	ps -ef | grep celery
	exit 0
else
	echo "plese su eoncloud first...."
	exit 1
fi



#!/bin/sh

cd /var/www/eoncloud_web/eoncloud_web/
../.venv/bin/celery multi stop eoncloud_worker --pidfile=/var/log/eoncloud/celery_%n.pid


ps -ef | grep celery

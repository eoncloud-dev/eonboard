# eonboard deploy step by step

## 1. os
>root@zhangh-ubuntu:~# cat /etc/lsb-release

	DISTRIB_ID=Ubuntu
	DISTRIB_RELEASE=14.10
	DISTRIB_CODENAME=utopic
	DISTRIB_DESCRIPTION="Ubuntu 14.10"

>cat /etc/apt/source.list

	deb http://mirrors.163.com/ubuntu/ utopic main restricted universe multiverse
	deb http://mirrors.163.com/ubuntu/ utopic-security main restricted universe multiverse
	deb http://mirrors.163.com/ubuntu/ utopic-updates main restricted universe multiverse
	deb http://mirrors.163.com/ubuntu/ utopic-proposed main restricted universe multiverse
	deb http://mirrors.163.com/ubuntu/ utopic-backports main restricted universe multiverse
	deb-src http://mirrors.163.com/ubuntu/ utopic main restricted universe multiverse
	deb-src http://mirrors.163.com/ubuntu/ utopic-security main restricted universe multiverse
	deb-src http://mirrors.163.com/ubuntu/ utopic-updates main restricted universe multiverse
	deb-src http://mirrors.163.com/ubuntu/ utopic-proposed main restricted universe multiverse
	deb-src http://mirrors.163.com/ubuntu/ utopic-backports main restricted universe multiverse

>apt-get update && apt-get upgrade

## 2. group and user

>groupadd eoncloud

>useradd eoncloud -g eoncloud -m -d /home/eoncloud

  	cat /etc/sudoers.d/eoncloud
	eoncloud ALL=(ALL) NOPASSWD:ALL

## 3. pip virtualenv

>apt-get install python-pip

>pip install virtualenv

## 4. install system dependences

>apt-get install apache2 mysql-client python-dev libffi-dev libssl-dev libmysqlclient-dev libapache2-mod-wsgi

    # if is all in one environment
    apt-get install mysql-server rabbitmq-server

## 5. config eoncloud_web
>cp eoncloud_web.tar.gz /var/www/

>tar zxvf eoncloud_web.tar.gz

	root@zhangh-ubuntu:/var/www/eoncloud_web# pwd
	/var/www/eoncloud_web

	root@zhangh-ubuntu:/var/www/eoncloud_web# tree -L 2
	.
	├── eoncloud_web
	│   ├── biz
	│   ├── cloud
	│   ├── eoncloud_web
	│   ├── manage.py
	│   └── render
	├── README
	└── requirements.txt

	root@zhangh-ubuntu:/var/www/eoncloud_web# virtualenv .venv
	root@zhangh-ubuntu:/var/www/eoncloud_web# .venv/bin/pip install -r requirements.txt

### create db and user

>create database cloud_web CHARACTER SET utf8;

>create user cloud_web;

>grant all privileges on cloud_web.* to 'cloud_web'@'%' identified by 'password' with grant option;

>flush privileges;

### generate local_settings.py

> root@zhangh-ubuntu:/var/www/eoncloud_web# cp eoncloud_web/eoncloud_web/local_settings.py.example \
> eoncloud_web/eoncloud_web/local_settings.py

### migrate db
>root@zhangh-ubuntu:/var/www/eoncloud_web# .venv/bin/python eoncloud_web/manage.py migrate

	# how migration works
	.venv/bin/python manage.py makemigrations app

### create super user

>root@zhangh-ubuntu:/var/www/eoncloud_web# .venv/bin/python eoncloud_web/manage.py createsuperuser

### init flavor

>root@zhangh-ubuntu:/var/www/eoncloud_web# .venv/bin/python eoncloud_web/manage.py init_flavor

### test web is ok

>root@zhangh-ubuntu:/var/www/eoncloud_web# .venv/bin/python eoncloud_web/manage.py runserver 0.0.0.0:8080

## 6. config apache2
>eoncloud@zhangh-ubuntu:~$ cat /etc/apache2/sites-available/000-default.conf

	<VirtualHost *:80>
	        ServerAdmin zhanghui@eoncloud.com.cn.

	        WSGIScriptAlias / /var/www/eoncloud_web/eoncloud_web/eoncloud.wsgi
	        WSGIDaemonProcess eoncloud user=eoncloud group=eoncloud processes=3 threads=10 python-path=/var/www/eoncloud_web/.venv/lib/python2.7/site-packages
	        WSGIProcessGroup eoncloud


	        Alias /static/admin /var/www/eoncloud_web/.venv/lib/python2.7/site-packages/django/contrib/admin/static/admin
	        Alias /static/rest_framework /var/www/eoncloud_web/.venv/lib/python2.7/site-packages/rest_framework/static/rest_framework
	        Alias /static /var/www/eoncloud_web/eoncloud_web/render/static

	        ErrorLog ${APACHE_LOG_DIR}/eoncloud_error.log
	        CustomLog ${APACHE_LOG_DIR}/eoncloud_access.log combined
	</VirtualHost>

	# vim: syntax=apache ts=4 sw=4 sts=4 sr noet


## 7. celery worker

>rabbitmqctl add_user eoncloud_web pAssw0rd

>rabbitmqctl add_vhost eoncloud

>rabbitmqctl set_permissions -p eoncloud eoncloud_web ".*" ".*" ".*"


	# sudo kill -9 `ps -ef | grep 'celery' | awk '{print $2}'`

	$ ../.venv/bin/celery multi start eoncloud_worker -A cloud --pidfile=/home/zhanghui/logs/eoncloud/celery_%n.pid --logfile=/home/zhanghui/logs/eoncloud/celery_%n.log

	$ ../.venv/bin/celery multi stop eoncloud_worker --pidfile=/home/zhanghui/logs/eoncloud/celery_%n.pid

## 8. integrity test

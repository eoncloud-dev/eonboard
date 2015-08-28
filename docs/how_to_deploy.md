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

>mkdir /var/log/eoncloud
>chown -R eoncloud:eoncloud /var/log/eoncloud

## 3. pip virtualenv

>apt-get install python-pip

>pip install virtualenv

## 4. install system dependences

>apt-get install apache2 mysql-client python-dev libffi-dev libssl-dev libmysqlclient-dev libapache2-mod-wsgi libldap2-dev libsasl2-dev

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
	│   ├── biz
	│   ├── cloud
	│   ├── eoncloud_web
	│   ├── manage.py
	│   └── render
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

> root@zhangh-ubuntu:/var/www/eoncloud_web# cp eoncloud_web/eoncloud_web/local/local_settings.py.example \
> eoncloud_web/eoncloud_web/local/local_settings.py

### migrate db
>root@zhangh-ubuntu:/var/www/eoncloud_web# .venv/bin/python eoncloud_web/manage.py migrate

	# how migration works
	.venv/bin/python manage.py makemigrations app

### create super user

>root@zhangh-ubuntu:/var/www/eoncloud_web# .venv/bin/python eoncloud_web/manage.py createsuperuser

    # admin/admin@mail.com

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

>rabbitmqctl add_user eoncloud_web password
>rabbitmqctl add_vhost eoncloud
>rabbitmqctl set_permissions -p eoncloud eoncloud_web ".*" ".*" ".*"

    su eoncloud
    run_celery.sh


## 8. integrity test

## 9. Advence feature
    
    0. 厂商名称： local_settings.BRAND = "EonCloud"
    1. ICP Number: local_settings.ICP_NUMBER = u"京ICP-123456YYY"
    2. 配额检查: local_settings.QUOTA_CHECK = True
    3. LDAP: local_settings.LDAP_AUTH_ENABLED = True
        3-1. LDAP Server
    4. 流程审批: local_settings.WORKFLOW_ENABLED = True
    5. 开放注册: local_settings.REGISTER_ENABLED = True
    6. 注册需要邮件激活: local_settings.REGISTER_ACTIVATE_EMAIL_ENABLED = True
        6-1. 激活邮件回调地址： local_settings.EXTERNAL_URL = 'http://www.xxx.com/'
    7. 是否开启图形验证码: local_settings.CAPTCHA_ENABLED = True
    8. 云主机监控: local_settings.MONITOR_ENABLED = True 
        8-1. base_url
    9. 备份

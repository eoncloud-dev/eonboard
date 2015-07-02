#-*-coding=utf-8-*-

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "cloud_web",
        'USER': "cloud_web",
        'PASSWORD': "password",
        'HOST': "127.0.0.1",
        'PORT': "3306",
        'TEST_CHARSET': 'utf8',
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB',
            }
    }
}

BROKER_URL = "amqp://eoncloud_web:pAssw0rd@127.0.0.1:5672/eoncloud"

# enabled quota check
QUOTA_CHECK = True

# sync instance status interval
INSTANCE_SYNC_INTERVAL_SECOND = 5
# max loop count for sync instance status
MAX_COUNT_SYNC  = 20


# site brand
BRAND = "EonCloud"
MCC = {
    "1" : u"金融",   
    "2" : u"军工",   
}
SOURCE = {
    "1": "InfoQ",
    "2": "CSDN",
}
USER_TYPE = {
    "1": u"个人用户",
    "2": u"企业用户",
}

QUOTA_ITEMS = {
    "instance": 0,
    "vcpu": 0,
    "memory": 0,
    "floating_ip": 0,
    "volume": 0,
    "volume_size": 0,
}

DEFAULT_NETWORK_NAME = u"默认网络"
DEFAULT_SUBNET_NAME = u"默认子网"
DEFAULT_ROUTER_NAME = u"默认路由"
DEFAULT_FIREWALL_NAME = u"默认防火墙"
OS_NAME_PREFIX = u"eon"

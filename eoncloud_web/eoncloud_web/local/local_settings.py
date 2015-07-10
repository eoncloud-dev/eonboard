#-*-coding=utf-8-*-


# sync instance status interval
INSTANCE_SYNC_INTERVAL_SECOND = 10
# max loop count for sync instance status
MAX_COUNT_SYNC  = 30


# enabled quota check
QUOTA_CHECK = True
MULTI_ROUTER_ENABLED = False

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

# quota items
QUOTA_ITEMS = {
    "instance": 0,
    "vcpu": 0,
    "memory": 0,
    "floating_ip": 0,
    "volume": 0,
    "volume_size": 0,
}

# default name
DEFAULT_NETWORK_NAME = u"默认网络"
DEFAULT_SUBNET_NAME = u"默认子网"
DEFAULT_ROUTER_NAME = u"默认路由"
DEFAULT_FIREWALL_NAME = u"默认防火墙"
OS_NAME_PREFIX = u"eon"

# backup config
RBD_COMPUTE_POOL = "compute"
RBD_VOLUME_POOL = "volumes"
BACKUP_RBD_HOST = "root@14.14.15.4:22"
BACKUP_RBD_HOST_PWD = "r00tme"
BACKUP_COMMAND_ARGS = {
    "source_pool": None,
    "image": None,
    "mode": None,
    "rbd_image": None,
    "dest_pool": "rbd",
    "dest_user": "root",
    "dest_host": "node-7",
}
BACKUP_COMMAND = "python /opt/eontools/rbd_backup.py  -p %(source_pool)s -i %(image)s -r %(dest_pool)s -u %(dest_user)s -d %(dest_host)s -o backup -m %(mode)s"

BACKUP_RESTORE_COMMAND = "python /opt/eontools/rbd_backup.py -p %(source_pool)s -i %(image)s -r %(dest_pool)s -u %(dest_user)s -d %(dest_host)s -o restore -s %(rbd_image)s"

BACKUP_DELETE_COMMAND = "python /opt/eontools/rbd_backup.py -p %(source_pool)s -i %(image)s -r %(dest_pool)s -u %(dest_user)s -d %(dest_host)s -o delete -s %(rbd_image)s"
# backup config end

SITE_CONFIG = {
    "QUOTA_CHECK" : QUOTA_CHECK,
    "MULTI_ROUTER_ENABLED" : MULTI_ROUTER_ENABLED,
    "BRAND": BRAND,
}

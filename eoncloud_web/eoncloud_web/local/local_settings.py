# -*-coding=utf-8-*-

# sync instance status interval
INSTANCE_SYNC_INTERVAL_SECOND = 10
# max loop count for sync instance status
MAX_COUNT_SYNC = 30


# enabled quota check
QUOTA_CHECK = True
MULTI_ROUTER_ENABLED = False

# site brand
BRAND = "EonCloud"
ICP_NUMBER = u"冀ICP备15016515号-1"

MCC = {
    "1": u"金融",
    "2": u"军工",
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
# openstack name format "{prefix}-{xxx}-{id}"
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
    "QUOTA_CHECK": QUOTA_CHECK,
    "MULTI_ROUTER_ENABLED": MULTI_ROUTER_ENABLED,
    "BRAND": BRAND,
    "ICP_NUMBER": ICP_NUMBER,
    "WORKFLOW_ENABLED": True
}

MONITOR_CONFIG = {
    "enabled": True,
    "base_url": "http://14.14.14.101:5601",
    'monitors': [
        {
            "title": u"CPU",
            "url": "/#/visualize/edit/cpu?embed&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'resource_id:!'{[{uuid}]}!'')),vis:(aggs:!((id:'1',params:(field:cpu_util),schema:metric,type:avg),(id:'2',params:(extended_bounds:(),field:'@timestamp',interval:{[{ interval }]},min_doc_count:1),schema:segment,type:date_histogram)),listeners:(),params:(addLegend:!f,addTooltip:!f,defaultYExtents:!f,shareYAxis:!t),type:line))"
        },
        {
            "title": u"磁盘",
            "url": "#/visualize/edit/disk?embed&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'resource_id:{[{uuid}]}')),vis:(aggs:!((id:'1',params:(field:disk.read.bytes),schema:metric,type:avg),(id:'2',params:(field:disk.write.bytes),schema:metric,type:avg),(id:'3',params:(extended_bounds:(),field:'@timestamp',interval:{[{interval}]},min_doc_count:1),schema:segment,type:date_histogram)),listeners:(),params:(addLegend:!t,addTooltip:!t,defaultYExtents:!f,shareYAxis:!t),type:line))"
        },
        {
            "title": u"网络",
            "url": "#/visualize/edit/network?embed&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'resource_id:{[{uuid}]}')),vis:(aggs:!((id:'1',params:(field:network.incoming.bytes.rate),schema:metric,type:avg),(id:'2',params:(field:network.outgoing.bytes.rate),schema:metric,type:avg),(id:'3',params:(extended_bounds:(),field:'@timestamp',interval:{[{interval}]},min_doc_count:1),schema:segment,type:date_histogram)),listeners:(),params:(addLegend:!t,addTooltip:!t,defaultYExtents:!f,shareYAxis:!t),type:line))"
        }
    ],
    'intervals': ['second', 'minute', 'hour', 'day', 'week', 'month']
}


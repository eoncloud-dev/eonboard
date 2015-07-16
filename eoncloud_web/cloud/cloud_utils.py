#-*-coding=utf-8-*-

RC_ENV = {
    "username": "username",
    "password": "password",
    "tenant_name": "tenant_name",
    "auth_url": "auth_url",
}


def _create_rc(obj=None):
    rc = RC_ENV.copy()

    rc["username"] = obj.user_data_center.keystone_user
    rc["password"] = obj.user_data_center.keystone_password
    rc["tenant_name"] = obj.user_data_center.tenant_name
    rc["tenant_uuid"] = obj.user_data_center.tenant_uuid
    rc["auth_url"] = obj.user_data_center.data_center.auth_url

    return rc


def create_rc_by_instance(instance=None):
    return _create_rc(instance)


def create_rc_by_network(network=None):
    return _create_rc(network)


def create_rc_by_subnet(subnet=None):
    return _create_rc(subnet)


def create_rc_by_router(router=None):
    return _create_rc(router)


def create_rc_by_volume(volume=None):
    return _create_rc(volume)


def create_rc_by_floating(floating=None):
    return _create_rc(floating)


def create_rc_by_udc(udc=None):
    rc = RC_ENV.copy()

    rc["username"] = udc.keystone_user
    rc["password"] = udc.keystone_password
    rc["tenant_name"] = udc.tenant_name
    rc["tenant_uuid"] = udc.tenant_uuid
    rc["auth_url"] = udc.data_center.auth_url

    return rc


def create_rc_by_dc(dc=None):
    rc = RC_ENV.copy()

    rc["username"] = dc.user
    rc["password"] = dc.password
    rc["tenant_name"] = dc.project
    rc["auth_url"] = dc.auth_url

    return rc


def create_rc_by_security(firewall=None):
    return _create_rc(firewall)


def create_rc_by_balancer_pool(pool=None):
    return _create_rc(pool)


def create_rc_by_balancer_member(member=None):
    return _create_rc(member)


def create_rc_by_balancer_vip(vip=None):
    return _create_rc(vip)


def create_rc_by_balancer_monitor(monitor=None):
    return _create_rc(monitor)
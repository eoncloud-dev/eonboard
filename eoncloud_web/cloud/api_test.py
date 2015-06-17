#-*-coding=utf-8-*- 
import logging

from biz.instance.models import Instance
from biz.instance.settings import INSTANCE_STATE_RUNNING
from biz.network.models import Network

from api import nova
from api import neutron
from api import keystone

LOG = logging.getLogger("cloud.tasks")

def flavor_create(request, instance):
    flavor = nova.flavor_create(request,
                                 name="flavor-%08d" % instance.id,
                                 memory=instance.memory,
                                 vcpu=instance.cpu,
                                 disk=instance.sys_disk,
                                 is_public=False)
    print flavor
    return flavor


def network_create(request):
    network_params = {'name': "network-04", "admin_state_up": True}
    network = neutron.network_create(request, **network_params)
    print network
    subnet_params = {"network_id": network.id,
                     "name": "subnet-04",
                     "cidr": "172.30.0.0/24",
                     "ip_version": 4,
                     #"gateway_ip": None, # is set none, disable gateway
                     "enable_dhcp": True}
    subnet = neutron.subnet_create(request, **subnet_params)
    print subnet
    return network


def instance_create(request, instance):
    nova.server_create(request,
                       name="instance-%08d" % instance.id,
                       image=instance.image,
                       flavor=instance.flavor_id,
                       key_name=None,
                       user_data=None,
                       security_groups=[],
                       nics=nics,
                       availability_zone="Nova",
                       admin_pass=instance.admin_pass)


def tenant_create():
    t = keystone.tenant_create(None, name="zhangh-test")
    print t
    return t

def user_create(t):
    u = keystone.user_create(None, name="zhangh",
                            email="zhangh@eoncloud.com",
                            password="admin",
                            project=t.id)

    roles = keystone.role_list(None)
    admin_role = filter(lambda r: r.name.lower() == "admin", roles)[0]
    keystone.add_tenant_user_role(None, project=t.id, user=u.id, role=admin_role.id)
    print u
    return u

def role_list():
    roles = keystone.role_list(None)
    print roles

def all_in_one():
    t = tenant_create()
    u = user_create(t)
    d = {"username": u.username,
         "password": "admin",
         "tenant_name": t.name,
         "auth_url": "http://14.14.14.100:5000/v2.0"}

    print d
    network = network_create(d)
    ins = Instance.objects.get(pk=2) 
    f = flavor_create(d, ins)
    print f
    nova.server_create(d, name="instance-%08d" % ins.id,
                image="1b21bcec-d8b3-4ad9-8f17-3b98f7d6adf6",
                flavor=f.id,
                key_name=None,
                user_data=None,
                security_groups=[],
                nics = [{"net-id": network.id, "v4-fixed-ip": ""}],
                availability_zone="nova",
                admin_pass="Eon!@#123"
                )

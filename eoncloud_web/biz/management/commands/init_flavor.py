#coding=utf-8

from django.core.management import BaseCommand

from biz.instance.models import Flavor


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        m1_micro  = Flavor()
        default_inst_types = {
            'm1.tiny': dict(mem=512, vcpus=1, root_gb=1, eph_gb=0, flavid=1),
            'm1.small': dict(mem=2048, vcpus=1, root_gb=20, eph_gb=0, flavid=2),
            'm1.medium': dict(mem=4096, vcpus=2, root_gb=40, eph_gb=0, flavid=3),
            'm1.large': dict(mem=8192, vcpus=4, root_gb=80, eph_gb=0, flavid=4),
            'm1.xlarge': dict(mem=16384, vcpus=8, root_gb=160, eph_gb=0, flavid=5)
            }

        for name, values in default_inst_types.iteritems():
            f = Flavor(name=name, memory=values["mem"], cpu=values["vcpus"], price=0)
            f.save()


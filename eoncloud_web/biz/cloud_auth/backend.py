#coding=utf-8


from django.contrib.auth.models import User, check_password 
from biz.cloud_auth.user import ComputeCenterUser as CCUser
from biz.computecenter.models import UserComputeCenter as UCC

class ComputeCenterBackend(object):

    def authenticate(self, username=None, password=None):
        user = None
        try:
            import pdb;pdb.set_trace();
            django_user = User.objects.get(username=username)
            pwd_valid = django_user.check_password(password)
            if pwd_valid:
                ucc = UCC.objects.filter(user=django_user)[0]
                user = CCUser(django_user) 
                user.set_user_compute_center(ucc)
                return user
        except User.DoesNotExist:
            pass
            
        return user

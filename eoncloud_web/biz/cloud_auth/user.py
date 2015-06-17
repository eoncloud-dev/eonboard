#coding=utf-8


from django.contrib.auth.models import User


class ComputeCenterUser(User):
    
    def set_user_compute_center(self, ucc):
        self.user_compute_center = ucc

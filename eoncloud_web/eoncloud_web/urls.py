"""eoncloud_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url, patterns
from django.contrib import admin

admin.autodiscover()

import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('biz.urls')),
]


urlpatterns += patterns('',
    url(r'^$', views.index, name="index"),
    url(r'^cloud/$', views.cloud, name="cloud"),
    url(r'^management/$', views.management, name="management"),

    # account
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^signup/$', 'biz.account.views.signup', name='signup'),
    url(r'^signup/success/$', 'biz.account.views.signup_success',
        name='signup_success'),
    url(r'^find-password/$', 'biz.account.views.find_password',
                                name="find_password"),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^current_user/$', views.current_user, name='current_user'),
    url(r'^no-udc/$', views.no_udc, name='no_udc'),
    url(r'^switch-idc/(?P<dc_id>[\d]+)$', views.switch_idc, name='switch_idc'),
    #url(r'^password-reset-complete/$',
    #                views.password_reset_complete,
    #                name="password_reset_complete")
)



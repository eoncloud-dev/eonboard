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

from frontend import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('biz.urls')),
    url(r'^captcha/', include('captcha.urls')),
]


urlpatterns += patterns(
    '',
    url(r'^$', views.index, name="index"),
    url(r'^cloud/$', views.cloud, name="cloud"),
    url(r'^management/$', views.management, name="management"),
    url(r'^state-service.js$', 'biz.common.views.state_service',
        name="state_service"),

    # account
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^signup/$', views.signup, name='signup'),

    url(r'^accounts/activate/(?P<code>.+)/$',
        views.first_activate_user,
        name='first_activate_user'),
    url(r'^accounts/resend-activate-email/$',
        views.resend_activate_email,
        name='resend_activate_email'),

    url(r'^find-password/$', views.find_password, name="find_password"),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^current_user/$', views.current_user, name='current_user'),
    url(r'^no-udc/$', views.no_udc, name='no_udc'),
    url(r'^switch-idc/(?P<dc_id>[\d]+)$', views.switch_idc, name='switch_idc'),
    #url(r'^password-reset-complete/$',
    #                views.password_reset_complete,
    #                name="password_reset_complete")
)



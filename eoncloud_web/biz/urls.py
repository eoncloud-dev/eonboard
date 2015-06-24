from django.conf.urls import patterns, include, url 
from rest_framework.urlpatterns import format_suffix_patterns


from biz.instance import views as instance_view
from biz.image import views as image_view
from biz.network import views as network_view
from biz.volume import views as volume_view
from biz.floating import views as floating_view

from biz.firewall import views as firewall_view
from biz.forum import views as forums_view
from biz.account import views as account_view

# instance&flavor
urlpatterns = [
        url(r'^instances/$', instance_view.InstanceList.as_view()),
        #url(r'^instances/(?P<pk>[0-9]+)/$', instance_view.InstanceDetail.as_view()),
        url(r'^instances/status/$', instance_view.instance_status_view),
        url(r'^instances/create/$', instance_view.instance_create_view),
        url(r'^instances/search/$', instance_view.instance_search_view),
        url(r'^instances/(?P<pk>[0-9]+)/action/$', instance_view.instance_action_view),
        url(r'^flavors/$', instance_view.FlavorList.as_view()),
        url(r'^flavors/(?P<pk>[0-9]+)/$', instance_view.FlavorDetail.as_view()),
    ]

# image
urlpatterns += format_suffix_patterns(
    [
        url(r'^images/$', image_view.ImageList.as_view()),
        url(r'^images/(?P<pk>[0-9]+)/$', image_view.ImageDetail.as_view()),
    ]
)

# network
urlpatterns += format_suffix_patterns(
    [
        url(r'^networks/$', network_view.network_list_view),
        url(r'^networks/create/$', network_view.network_create_view),
        url(r'^networks/status/$', network_view.network_status_view),
        url(r'^networks/delete/$', network_view.delete_action),
        url(r'^networks/router/action$', network_view.network_attach_router_view),
        url(r'^networks/topology/$', network_view.network_topology_data_view),
    ]
)

# router
urlpatterns += format_suffix_patterns(
    [
        url(r'^routers/$', network_view.router_list_view),
        url(r'^routers/create/$', network_view.router_create_view),
        url(r'^routers/delete/$', network_view.router_delete_view),
        url(r'^routers/search/$', network_view.router_search_view),
    ]
)

# volume
urlpatterns += format_suffix_patterns(
    [
        url(r'^volumes/$', volume_view.volume_list_view),
        url(r'^volumes/search/$', volume_view.volume_list_view_by_instance),
        url(r'^volumes/create/$', volume_view.volume_create_view),
        url(r'^volumes/update/$', volume_view.volume_update_view),
        url(r'^volumes/action/$', volume_view.volume_action_view),
        url(r'^volumes/status/$', volume_view.volume_status_view),
    ]
)

# floating
urlpatterns += format_suffix_patterns(
    [
        url(r'^floatings/$', floating_view.list_view),
        #url(r'^floatings/search/$', floating_view.volume_list_view_by_instance),
        #url(r'^floatings/update/$', floating_view.volume_update_view),
        url(r'^floatings/create/$', floating_view.create_view),
        url(r'^floatings/action/$', floating_view.floating_action_view),
        url(r'^floatings/status/$', floating_view.floating_status_view),
    ]
)

# FIREWALL
urlpatterns += format_suffix_patterns(
    [
        url(r'^firewall/$', firewall_view.firewall_list_view),
        url(r'^firewall/create/$', firewall_view.firewall_create_view),
        url(r'^firewall/delete/$', firewall_view.firewall_delete_view),
        url(r'^firewall/firewall_rules/(?P<firewall_id>[0-9]+)/$', firewall_view.firewall_rule_list_view),
        url(r'^firewall/firewall_rules/create/$', firewall_view.firewall_rule_create_view),
        url(r'^firewall/firewall_rules/delete/$', firewall_view.firewall_rule_delete_view),
        url(r'^firewall/default_rules/$', firewall_view.firewall_rule_view),
        url(r'^firewall/server_change_firewall/$', firewall_view.instance_change_firewall_view),
    ]
)

# account
urlpatterns += format_suffix_patterns(
    [
        url(r'^account/contract/$', account_view.contract_view),
        url(r'^account/quota/$', account_view.quota_view),
        url(r'^operation/$', account_view.OperationList.as_view()),
    ]
)

# forum
urlpatterns += format_suffix_patterns(
    [
        url(r'^forums/$', forums_view.forum_list_view),
        url(r'^forums/create/$', forums_view.forum_create_view),
        url(r'^forums/delete/$', forums_view.forum_create_view),
        url(r'^forums/close/$', forums_view.forum_close_forum_view),
        url(r'^forums/reply/create/$', forums_view.forum_reply_create_view),
        url(r'^forums/reply/$', forums_view.forum_reply_list_view),
    ]
)

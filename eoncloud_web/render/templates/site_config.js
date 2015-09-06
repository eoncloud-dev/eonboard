angular.module('cloud.services')
    .constant('site_config', {{site_config|safe}})
    .constant('current_user', {{current_user|safe}});

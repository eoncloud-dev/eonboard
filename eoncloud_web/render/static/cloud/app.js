/**
 * Created by zhanghui
 * Author: zhanghui9700@gmail.com
 * Date: 2015-05-04
 * Description: Main Cloud App
 */

'use strict';

/* Cloud App */
var CloudApp = angular.module("CloudApp", [
    "ui.router",
    "ui.bootstrap",
    "oc.lazyLoad",
    "ngSanitize",
    "ngTable",
    "ngResource",
    "ngCookies",
    "jm.i18next",
    "cloud.services",
    "cloud.resources",
    "cloud.directives"
]);

CloudApp.config(function ($i18nextProvider) {
    $i18nextProvider.options = {
        lng: 'cn',
        fallbackLng: 'en',
        useCookie: false,
        useLocalStorage: false,
        resGetPath: '/static/cloud/locales/__lng__/__ns__.json'
    };
});

CloudApp.config(['$resourceProvider', function ($resourceProvider) {
    $resourceProvider.defaults.stripTrailingSlashes = false;
}]);

CloudApp.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol("{[{");
    $interpolateProvider.endSymbol("}]}");
}]);

CloudApp.config(['$httpProvider', function ($httpProvider) {
    $httpProvider.defaults.useXDomain = true;
    delete $httpProvider.defaults.headers.common['X-Request-Width'];
    $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8';
    $httpProvider.interceptors.push('AuthInterceptor');
}]);

CloudApp.config(['$ocLazyLoadProvider', function ($ocLazyLoadProvider) {
    $ocLazyLoadProvider.config({});
}]);

/* Setup App Main Controller */
CloudApp.controller('AppController', ['$scope', '$rootScope', function ($scope, $rootScope) {
    $scope.$on('$viewContentLoaded', function () {
        Metronic.initComponents(); // init core components
    });
}]);

/***
 Layout Partials.
 By default the partials are loaded through AngularJS ng-include directive. In case they loaded in server side(e.g: PHP include function) then below partial
 initialization can be disabled and Layout.init() should be called on page load complete as explained above.
 ***/

/* Setup Layout Part - Header */
CloudApp.controller('HeaderController', ['$rootScope', '$scope', '$http', function ($rootScope, $scope, $http) {
    $scope.$on('$includeContentLoaded', function () {
        Layout.initHeader(); // init header
    });

    $http({"method": "GET", "url": "/current_user/"}).success(function (data) {
        $rootScope.current_user = data;
    });
}]);

/* Setup Layout Part - Sidebar */
CloudApp.controller('SidebarController', ['$scope', function ($scope) {
    $scope.$on('$includeContentLoaded', function () {
        Layout.initSidebar(); // init sidebar
    });
}]);

/* Setup Layout Part - Footer */
CloudApp.controller('FooterController', ['$scope', function ($scope) {
    $scope.$on('$includeContentLoaded', function () {
        Layout.initFooter(); // init footer
    });
}]);


/* Setup Rounting For All Pages */
CloudApp.config(['$stateProvider', '$urlRouterProvider',
    function ($stateProvider, $urlRouterProvider, $stateParams) {
        $urlRouterProvider.otherwise("/overview/");

        $stateProvider
            // Overview
            .state('overview', {
                url: "/overview/",
                templateUrl: "/static/cloud/views/overview.html",
                data: {pageTitle: 'Overview'},
                controller: "OverviewController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/assets/admin/pages/css/timeline.css',
                                '/static/cloud/controllers/overview_ctl.js'
                            ]
                        });
                    }],
                    contract: function (CommonHttpService) {
                        return CommonHttpService.get("/api/account/contract/");
                    },
                    quota: function (CommonHttpService) {
                        return CommonHttpService.get("/api/account/quota/");
                    }
                }
            })

            // instance
            .state("instance", {
                url: "/instance/",
                templateUrl: "/static/cloud/views/instance.html",
                data: {pageTitle: 'Instance'},
                controller: "InstanceController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/assets/global/plugins/bootstrap-wizard/jquery.bootstrap.wizard.min.js',
                                '/static/cloud/scripts/create_instance_wizard.js',
                                '/static/cloud/controllers/instance_ctl.js'
                            ]
                        });
                    }],
                    status_desc: function (CommonHttpService) {
                        return CommonHttpService.get("/api/instances/status/")
                    }
                }

            })

            // image
            .state("image", {
                url: "/image/",
                templateUrl: "/static/cloud/views/image.html",
                data: {pageTitle: 'Image'},
                controller: "ImageController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/cloud/controllers/image_ctl.js'
                            ]
                        });
                    }]
                }
            })

            // volume
            .state("volume", {
                url: "/volume/",
                templateUrl: "/static/cloud/views/volume.html",
                data: {pageTitle: 'Volume'},
                controller: "VolumeController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [

                                '/static/cloud/controllers/volume_ctl.js'
                            ]
                        });
                    }],
                    status_desc: function (CommonHttpService) {
                        return CommonHttpService.get("/api/volumes/status/")
                    }
                }
            })

            // floating ip
            .state("floating", {
                url: "/floating/",
                templateUrl: "/static/cloud/views/floating.html",
                data: {pageTitle: 'FloatingIP'},
                controller: "FloatingController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [

                                '/static/cloud/controllers/floating_ctl.js'
                            ]
                        });
                    }],
                    status_desc: function (CommonHttpService) {
                        return CommonHttpService.get("/api/floatings/status/")
                    }
                }
            })

            // firewall
            .state("firewall", {
                url: "/firewall/",
                templateUrl: "/static/cloud/views/firewall.html",
                data: {pageTitle: 'Firewall'},
                controller: "FirewallController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/cloud/controllers/firewall_ctl.js'
                            ]
                        });
                    }]
                }
            })

            // firewall.addrule
            .state("firewallrules", {
                url: "/firewallrules/:firewall_id",
                templateUrl: "/static/cloud/views/firewall_rules.html",
                data: {pageTitle: 'Firewall'},
                controller: "FirewallRulesController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/cloud/controllers/firewall_ctl.js'
                            ]
                        });
                    }],
                    firewall_id: function ($stateParams) {
                        return $stateParams.firewall_id;
                    }
                }
            })

            // network
            .state("network", {
                url: "/network/",
                templateUrl: "/static/cloud/views/network.html",
                data: {pageTitle: 'Firewall'},
                controller: "NetworkController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/cloud/controllers/network_ctl.js'
                            ]
                        });
                    }],
                    status_desc: function (CommonHttpService) {
                        return CommonHttpService.get("/api/networks/status/")
                    }
                }
            })

            // router
            .state("router", {
                url: "/router/",
                templateUrl: "/static/cloud/views/router.html",
                data: {pageTitle: 'Firewall'},
                controller: "RouterController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [

                                '/static/cloud/controllers/router_ctl.js'
                            ]
                        });
                    }],
                    status_desc: function (CommonHttpService) {
                        return CommonHttpService.get("/api/networks/status/")
                    }
                }
            })
            // load balancer
            .state("lbaas", {
                url: "/lbaas/",
                templateUrl: "/static/cloud/views/loadbalancer.html",
                data: {pageTitle: 'LoadBalancer'},
                controller: "LoadBalancerController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [

                                '/static/cloud/controllers/loadbalancer_ctl.js'
                            ]
                        });
                    }],
                    status_desc:function(CommonHttpService){
                        return CommonHttpService.get("/api/lbs/status/")
                    }
                }
            })
            // load balancer
            .state("lbaasinfo", {
                url: "/lbaas/:balancer_id",
                templateUrl: "/static/cloud/views/loadbalancer_info.html",
                data: {pageTitle: 'LoadBalancer'},
                controller: "LoadBalancerInfoController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [

                                '/static/cloud/controllers/loadbalancer_ctl.js'
                            ]
                        });
                    }],
                    balancer_id:function($stateParams) {
                        return $stateParams.balancer_id;
                    },
                    status_desc:function(CommonHttpService){
                        return CommonHttpService.get("/api/lbs/status/")
                    }
                }
            })
            // router
            .state("topology", {
                url: "/topology/",
                templateUrl: "/static/cloud/views/network_topology.html",
                data: {pageTitle: 'Network topology'},
                controller: "NetworkTopologyController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                "/static/assets/admin/layout/css/network_topology.css",
                                "/static/assets/admin/layout/scripts/horizon.js",
                                "/static/assets/admin/layout/scripts/d3.v3.min.js",
                                "/static/assets/admin/layout/scripts/hogan-2.0.0.js",
                                "/static/assets/admin/layout/scripts/horizon.networktopology.js",
                                "/static/cloud/controllers/network_ctl.js"
                            ]
                        });
                    }]
                }
            })
            // forum
            .state("forum", {
                url: "/forum/",
                templateUrl: "/static/cloud/views/forum.html",
                data: {pageTitle: 'forum'},
                controller: "ForumController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [

                                '/static/cloud/controllers/forum_ctl.js'
                            ]
                        });
                    }]
                }
            })
            // operation
            .state("operation", {
                url: "/operation/",
                templateUrl: "/static/cloud/views/operation.html",
                data: {pageTitle: 'Operation'},
                controller: "OperationController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/assets/global/plugins/bootstrap-datepicker/css/datepicker3.css',
                                '/static/assets/global/plugins/bootstrap-datepicker/js/bootstrap-datepicker.js',
                                '/static/cloud/controllers/operation_ctl.js'
                            ]
                        });
                    }]
                }
            })
            // backup
            .state("backup", {
                url: "/backup/",
                templateUrl: "/static/cloud/views/backup.html",
                data: {pageTitle: 'Backup'},
                controller: "BackupController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/cloud/controllers/backup_ctl.js'
                            ]
                        });
                    }],
                    status_desc: function(CommonHttpService){
                        return CommonHttpService.get("/api/backup/status/");
                    }
                }
            })
        ;
    }]);
CloudApp.factory('ValidationTool', function(){

    var defaultConfig = {
        onkeyup: false,
        doNotHideMessage: true,
        errorElement: 'span',
        errorClass: 'help-block help-block-error',
        focusInvalid: false,
        errorPlacement: function (error, element) {
            error.insertAfter($(element).closest('.input-group'));
        },

        highlight: function (element) {
            $(element).closest('.form-group').removeClass('has-success').addClass('has-error');
        },

        unhighlight: function (element) {
            $(element).closest('.form-group').removeClass('has-error').addClass('has-success');
        }
    };

    return {
        init: function(selector, config){
            for(var attr in defaultConfig){
                if(config[attr] === undefined){
                    config[attr] = defaultConfig[attr];
                }
            }
            $(selector).validate(config);

            return $(selector);
        }
    }
});

/* Init global settings and run the app */
CloudApp.run(["$rootScope", "settings", "$state", "$http", "$cookies", "$interval", "CommonHttpService",
    function ($rootScope, settings, $state, $http, $cookies, $interval, CommonHttpService) {
        $http.defaults.headers.common['X-CSRFToken'] = $cookies['csrftoken'];
        $rootScope.$state = $state;
        $rootScope.timer_list = [];
        var callbacks = [];

        $rootScope.executeWhenLeave = function(callback){
            callbacks.push(callback);
        };

        $rootScope.$on("$stateChangeStart", function (e, toState, toParams, fromState, fromParams) {
            while ($rootScope.timer_list.length > 0) {
                var t = $rootScope.timer_list.pop();
                $interval.cancel(t);
            }

            while(callbacks.length > 0){
                var callback = callbacks.pop();
                callback();
            }
        });

        CommonHttpService.get("/api/account/site-config/").then(function(data){
            $rootScope.site_config = data;
        });
    }]);

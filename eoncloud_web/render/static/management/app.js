/**
 * Created by zhanghui
 * Author: zhanghui9700@gmail.com
 * Date: 2015-05-04
 * Description: Main Cloud App
 */

'use strict';

function template(name){
    return "/static/management/views/" + name + ".html";
}
/* Cloud App */
var CloudApp = angular.module("CloudApp", [
    "ui.router",
    "ui.bootstrap",
    "oc.lazyLoad",
    "ngSanitize",
    "ngTable",
    "ngResource",
    "ngCookies",
    "ngBootbox",
    "jm.i18next",
    "ngLodash",
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

CloudApp.config(['$httpProvider', function($httpProvider){
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
CloudApp.controller('HeaderController', ['$rootScope', '$scope', '$http', 'passwordModal',
    function ($rootScope, $scope, $http, passwordModal) {

        $scope.$on('$includeContentLoaded', function () {
            Layout.initHeader(); // init header
        });

        $http({"method": "GET", "url": "/current_user/"}).success(function (data) {
            $rootScope.current_user = data;
        });

        $scope.passwordModal = passwordModal;
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
    function ($stateProvider, $urlRouterProvider,$stateParams) {
        $urlRouterProvider.otherwise("/overview/");

        $stateProvider
            // Overview
            .state('overview', {
                url: "/overview/",
                templateUrl: template('overview'),
                data: {pageTitle: 'Overview'},
                controller: "OverviewController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/assets/admin/pages/css/timeline.css',
                                '/static/management/controllers/overview_ctl.js'
                            ]
                        });
                    }],
                    summary: function(CommonHttpService){
                        return CommonHttpService.get("/api/management-summary/");
                    }
                }
            })

            // contract
            .state("contract", {
                url: "/contract/",
                templateUrl: template('contract'),
                data: {pageTitle: "Contract"},
                controller: "ContractController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/assets/global/plugins/bootstrap-datepicker/css/datepicker3.css',
                                '/static/assets/global/plugins/bootstrap-datepicker/js/bootstrap-datepicker.js',
                                '/static/management/controllers/contract_ctrl.js'
                            ]
                        });
                    }]
                }
            })

            // data center
            .state("data_center", {
                url: "/data-center/",
                templateUrl: template('data_center'),
                data: {pageTitle: "Data Center"},
                controller: "DataCenterController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/management/controllers/data_center_ctrl.js'
                            ]
                        });
                    }]
                }
            })

            // data center
            .state("flavor", {
                url: "/flavor/",
                templateUrl: template('flavor'),
                data: {pageTitle: "Flavor"},
                controller: "FlavorController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/management/controllers/flavor_ctrl.js'
                            ]
                        });
                    }]
                }
            })

            // image
            .state("image", {
                url: "/image/",
                templateUrl: "/static/management/views/image.html",
                data: {pageTitle: 'Image'},
                controller: "ImageController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/management/controllers/image_ctrl.js'
                            ]
                        });
                    }]
                }
            })

            // forum
            .state("forum", {
                url: "/support/",
                templateUrl: "/static/management/views/forum.html",
                data: {pageTitle: 'Forum'},
                controller: "ForumController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/management/controllers/forum_ctrl.js'
                            ]
                        });
                    }]
                }
            })
            // operation
            .state("operation", {
                url: "/operation/",
                templateUrl: "/static/management/views/operation.html",
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
                                '/static/management/controllers/operation_ctl.js'
                            ]
                        });
                    }]
                }
            })

            // user
            .state("user", {
                url: "/users/",
                templateUrl: "/static/management/views/user.html",
                data: {pageTitle: 'User'},
                controller: "UserController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/management/controllers/user_ctrl.js'
                            ]
                        });
                    }]
                }
            })

            // user
            .state("notifications", {
                url: "/notifications/",
                templateUrl: "/static/management/views/notification.html",
                data: {pageTitle: 'Notification'},
                controller: "NotificationController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/management/controllers/notification_ctrl.js'
                            ]
                        });
                    }]
                }
            })

            // workflow
            .state("workflow", {
                url: "/workflow/",
                templateUrl: "/static/management/views/workflow.html",
                data: {pageTitle: 'Workflow Definition'},
                controller: "WorkflowManagementController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/management/controllers/workflow_ctrl.js'
                            ]
                        });
                    }]
                }
            });
    }]);

/* Init global settings and run the app */
CloudApp.run(["$rootScope", "settings", "$state", "$http", "$cookies", "$interval", "CommonHttpService",
    function ($rootScope, settings, $state, $http, $cookies, $interval, CommonHttpService) {
        $http.defaults.headers.common['X-CSRFToken'] = $cookies['csrftoken'];
        $rootScope.$state = $state;
        var callbacks = [];

        $rootScope.executeWhenLeave = function(callback){
            callbacks.push(callback);
        };

        $rootScope.setInterval = function(func, interval){
            var timer = $interval(func, interval);

            $rootScope.executeWhenLeave(function(){
                $interval.cancel(timer);
            });
        };

        $rootScope.$on("$stateChangeStart", function (e, toState, toParams, fromState, fromParams) {

            angular.forEach(callbacks, function(callback){
                callback();
            });

            callbacks = [];
        });

        CommonHttpService.get("/api/account/site-config/").then(function(data){
            $rootScope.site_config = data;
        });
    }]);
'use strict';

CloudApp.controller('OverviewController',
    function ($rootScope, $scope, Operation, Notification, contract, quota) {
        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;

        $scope.contract = contract;
        $scope.quota = quota;

        $scope.operation_icon = function (op) {
            var op_icon_mapping = {
                'Instance': 'icon-rocket',
                'Network': 'icon-equalizer',
                'Floating': 'icon-globe',
                'Firewall': 'icon-shield',
                'FirewallRules': 'icon-vector',
                'Backup': 'icon-layers',
                'Volume': 'icon-disc',
                'BalancerPool': 'icon-social-dropbox',
                'BalancerMember': 'icon-users',
                'BalancerVIP': 'icon-globe',
                'BalancerMonitor': 'icon-eye',
                'Router': 'icon-size-fullscreen'
            };

            if(op.resource in op_icon_mapping) {
                return op_icon_mapping[op.resource];
            }
            else {
                return "icon-bulb";
            }
        };

        Operation.query({page_size: 6}, function (data) {
            $scope.operation_list = data.results;
        });

        Notification.status(function(status){
            $scope.notificationNum = status.num;
        })
    });

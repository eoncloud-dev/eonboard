'use strict';

CloudApp.controller('OverviewController',
    function ($rootScope, $scope, contract, quota) {
        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;


        $scope.contract = contract;

        $scope.quota =  quota;
    });

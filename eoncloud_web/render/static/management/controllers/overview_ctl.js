'use strict';

CloudApp.controller('OverviewController',
    function ($rootScope, $scope, instanceSummary, accountSummary) {
        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;


        $scope.instanceSummary = instanceSummary;

        $scope.accountSummary =  accountSummary;

    });

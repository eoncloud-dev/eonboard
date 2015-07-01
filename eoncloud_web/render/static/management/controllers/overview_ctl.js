'use strict';

CloudApp.controller('OverviewController',
    function ($rootScope, $scope, summary) {
        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;

        $scope.summary =  summary;

    });

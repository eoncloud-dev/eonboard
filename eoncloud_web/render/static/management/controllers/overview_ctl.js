'use strict';

CloudApp.controller('OverviewController',
    function ($rootScope, $scope, summary) {
        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        $scope.summary =  summary;

    });

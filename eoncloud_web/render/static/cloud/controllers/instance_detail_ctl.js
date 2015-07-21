'use strict';


CloudApp.controller('InstanceDetailController',
    function ($rootScope, $scope, $filter, $timeout, ngTableParams, instance) {
        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;

        $scope.instance = instance;
    });

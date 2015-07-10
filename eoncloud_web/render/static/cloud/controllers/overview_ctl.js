'use strict';

CloudApp.controller('OverviewController',
    function ($rootScope, $scope, contract, Operation, quota) {
        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;


        $scope.contract = contract;

        $scope.quota =  quota;

        Operation.query({page_size: 6}, function(data){
            $scope.operation_list = data.results;
        });
    });

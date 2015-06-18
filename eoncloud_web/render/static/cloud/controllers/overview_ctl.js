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

        Operation.query(function(data){
            if(data && data.length > 6) {
                $scope.operation_list = data.slice(0, 6);
            }
            else{
                $scope.operation_list = data;
            }
        });
    });

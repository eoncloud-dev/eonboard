'use strict';

CloudApp.controller('OperationController', function($rootScope, $scope, $filter, $timeout, ngTableParams, Operation) {
    $scope.$on('$viewContentLoaded', function() {   
        Metronic.initAjax();
    });

    $rootScope.settings.layout.pageBodySolid = true;
    $rootScope.settings.layout.pageSidebarClosed = false;

    $scope.operation_table = new ngTableParams({
        page: 1,
        count: 10
    },{
        counts: [],
        getData: function ($defer, params) {
            Operation.query(function (data) {
                var data_list = params.sorting() ?
                    $filter('orderBy')(data, params.orderBy()) : volume.name;
                params.total(data_list.length);
                $defer.resolve(data_list.slice((params.page() - 1) * params.count(), params.page() * params.count()));
            });
        }
    });
});

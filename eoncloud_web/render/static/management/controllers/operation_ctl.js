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
        counts: [10, 20, 30, 40, 50],
        getData: function ($defer, params) {

            Operation.query({page: params.page(), page_size: params.count()},
                function (data) {
                    params.total(data.count);
                    $defer.resolve(data.results);
                });
        }
    });
});

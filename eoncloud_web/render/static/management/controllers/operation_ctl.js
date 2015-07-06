'use strict';

CloudApp.controller('OperationController', function($rootScope, $scope, $filter, $timeout, ngTableParams, Operation) {
    $scope.$on('$viewContentLoaded', function() {   
        Metronic.initAjax();
    });

    $rootScope.settings.layout.pageBodySolid = true;
    $rootScope.settings.layout.pageSidebarClosed = false;

    $scope.filterEnabled = true;

    $scope.toggleFilter = function(){
        $scope.filterEnabled = !$scope.filterEnabled;
    };

    $scope.operation_table = new ngTableParams({
        page: 1,
        count: 10,
        filter: {
            resource_i18n: '',
            operator: '',
            data_center_name: ''
        }
    },{
        counts: [],
        getData: function ($defer, params) {
            Operation.query(function (data) {

                var data_list =  data;

                if(params.filter()){
                    data_list = $filter('filter')(data_list, params.filter());
                }

                if (params.sorting()){
                    data_list = $filter('orderBy')(data_list, params.orderBy());
                }

                params.total(data_list.length);
                $defer.resolve(data_list.slice((params.page() - 1) * params.count(), params.page() * params.count()));
            });
        }
    });
});

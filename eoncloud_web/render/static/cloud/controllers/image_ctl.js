'use strict';

CloudApp.controller('ImageController', function($rootScope, $scope, $filter, $timeout, ngTableParams, Image) {
    $scope.$on('$viewContentLoaded', function() {   
        Metronic.initAjax();
    });

    $scope.image_table = new ngTableParams({
        page: 1,
        count: 10
    },{
        counts: [],
        getData: function ($defer, params) {
            Image.query(function (data) {
                var data_list = params.sorting() ?
                    $filter('orderBy')(data, params.orderBy()) : volume.name;
                params.total(data_list.length);
                $scope.current_image_data = data_list.slice((params.page() - 1) * params.count(), params.page() * params.count());
                $defer.resolve($scope.current_image_data);
            });
        }
    });
});

'use strict';

CloudApp.controller('RouterController', function($rootScope, $scope, $filter, $timeout,$interval,$i18next, $modal,ngTableParams,Router,status_desc,CommonHttpService,ToastrService) {
    $scope.$on('$viewContentLoaded', function() {   
        Metronic.initAjax();
    });

    $rootScope.settings.layout.pageBodySolid = true;
    $rootScope.settings.layout.pageSidebarClosed = false;

    $scope.status_desc = status_desc;
    console.log(status_desc)
    $scope.isNetwork = function (isNetwork){
        if(isNetwork==true){
            return '是';
        }else{
            return '否';
        }
    }

    $scope.current_router_data = [];

    $scope.router_table = new ngTableParams({
        page: 1,
        count: 10
    }, {
        counts: [],
        getData: function ($defer, params) {
            Router.query(function (data) {
                var data_list = params.sorting() ?
                    $filter('orderBy')(data, params.orderBy()) : "";
                params.total(data_list.length);
                $scope.current_router_data = data_list.slice((params.page() - 1) * params.count(), params.page() * params.count());
                $defer.resolve($scope.current_router_data);
            });
        }
    });
    //定时处理路由状态
    var timer = $interval(function () {
        var list = $scope.current_router_data;
        var need_refresh = false;
        for (var i = 0; i < list.length; i++) {
            if (status_desc[list[i].status][1] == 0) {
                need_refresh = true;
                break;
            }
        }
        if (need_refresh) {
            $scope.router_table.reload();
        }

    }, 5000);
    $rootScope.timer_list.push(timer);
    /////////////////////////
    $scope.checkboxes = {'checked': false, items: {}};

    // watch for check all checkbox
    $scope.$watch('checkboxes.checked', function (value) {
        angular.forEach($scope.current_router_data, function (item) {
            if($scope.status_desc[item.status][1]==1){
                if (angular.isDefined(item.id)) {
                    $scope.checkboxes.items[item.id] = value;
                }
            }
        });
    });

    // watch for data checkboxes
    $scope.$watch('checkboxes.items', function (values) {
        $scope.checked_count = 0;
        if (!$scope.current_router_data) {
            return;
        }
        var checked = 0, unchecked = 0,
            total = $scope.current_router_data.length;

        angular.forEach($scope.current_router_data, function (item) {
            if($scope.status_desc[item.status][1]==0){
                $scope.checkboxes.items[item.id] = false;
            }
            checked += ($scope.checkboxes.items[item.id]) || 0;
            unchecked += (!$scope.checkboxes.items[item.id]) || 0;
        });
        if ((unchecked == 0) || (checked == 0)) {
            $scope.checkboxes.checked = ((checked == total) && total != 0);
        }

        $scope.checked_count = checked;
        // grayed checkbox
        angular.element(document.getElementById("select_all")).prop("indeterminate", (checked != 0 && unchecked != 0));
    }, true);
    ////////////////////////
    $scope.modal_create_router = function(){
        $scope.router = "";
        $scope.operation = 'create';
        $modal.open({
            templateUrl: 'router_create.html',
            controller: 'RouterCreateController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                router_table: function () {
                    return $scope.router_table;
                }
            }
        });

    }

    $scope.batch_action = function(action){
        bootbox.confirm($i18next("network.confirm_" + action), function (confirm) {
            if (confirm) {
                var items = $scope.checkboxes.items;
                var items_key = Object.keys(items);
                for (var i = 0; i < items_key.length; i++) {
                    if (items[items_key[i]]) {
                        var post_data = {
                            "router_id":items_key[i]
                        }
                        CommonHttpService.post("/api/routers/delete/", post_data).then(function (data) {
                            if (data.OPERATION_STATUS == 1) {
                                $scope.router_table.reload();
                            }
                            else {
                                ToastrService.error(data.MSG, $i18next("op_failed"));
                            }
                        });
                        $scope.checkboxes.items[items_key[i]] = false;
                    }
                }
            }
        });
    }
    $scope.modal_edit_router = function(router){
        $scope.router = {
            "id":router.id,
            "name":router.name,
            "is_gateway":router.is_gateway
        };
        $scope.operation = 'edit';
        $modal.open({
            templateUrl: 'router_create.html',
            controller: 'RouterCreateController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                router_table: function () {
                    return $scope.router_table;
                }
            }
        });

    }

});


CloudApp.controller('RouterCreateController',
    function($rootScope, $scope, $filter, $modalInstance,$i18next,CommonHttpService,ToastrService,router_table) {
        $scope.has_error=false;

        $scope.router_create = {},
        $scope.cancel = function () {
            $modalInstance.dismiss();
        };

        $scope.submit_click = function(router){
            if(typeof(router.name) =='undefined' || router.name==''){
                $scope.has_error=true;
                return ;
            }
            var post_data = {
                "id":router.id,
                "name":router.name,
                "is_gateway":typeof(router.is_gateway) =='undefined'?false:router.is_gateway
            }
            CommonHttpService.post("/api/routers/create/", post_data).then(function (data) {
                if (data.OPERATION_STATUS == 1) {
                    ToastrService.success(data.MSG, $i18next("success"));
                    router_table.reload();
                }
                else {
                    ToastrService.error(data.MSG, $i18next("op_failed"));
                }
                $modalInstance.dismiss();
            });
        }
    });

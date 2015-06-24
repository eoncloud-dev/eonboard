'use strict';

CloudApp.controller('NetworkController', function($rootScope, $scope, $filter, $timeout,$interval,$i18next, ngTableParams,$modal,CommonHttpService,ToastrService, Network,status_desc) {
    $scope.$on('$viewContentLoaded', function() {   
        Metronic.initAjax();
    });

    $rootScope.settings.layout.pageBodySolid = true;
    $rootScope.settings.layout.pageSidebarClosed = false;
    $scope.status_desc = status_desc

    $scope.current_network_data = [];
    $scope.network_table = new ngTableParams({
        page: 1,
        count: 10
    }, {
        counts: [],
        getData: function ($defer, params) {
            Network.query(function (data) {
                var data_list = params.sorting() ?
                    $filter('orderBy')(data, params.orderBy()) : "";
                params.total(data_list.length);
                $scope.current_network_data = data_list.slice((params.page() - 1) * params.count(), params.page() * params.count());
                $defer.resolve($scope.current_network_data);
            });
        }
    });
    //定时处理网络状态
    var timer = $interval(function () {
        var list = $scope.current_network_data;
        var need_refresh = false;
        for (var i = 0; i < list.length; i++) {
            if (status_desc[list[i].status][1] == 0) {
                need_refresh = true;
                break;
            }
        }
        if (need_refresh) {
            $scope.network_table.reload();
        }

    }, 5000);
    $rootScope.timer_list.push(timer);
    /////////////////////////
    $scope.checkboxes = {'checked': false, items: {}};

    // watch for check all checkbox
    $scope.$watch('checkboxes.checked', function (value) {
        angular.forEach($scope.current_network_data, function (item) {
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
        if (!$scope.current_network_data) {
            return;
        }
        var checked = 0, unchecked = 0,
            total = $scope.current_network_data.length;

        angular.forEach($scope.current_network_data, function (item) {
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

    $scope.modal_create_network = function(){
        $scope.network_create = '';
        $scope.operation = 'create';
        $modal.open({
            templateUrl: 'network_create.html',
            controller: 'NetworkCreateController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                network_table: function () {
                    return $scope.network_table;
                }
            }
        });

    }


    $scope.modal_edit_network = function(network){
        $scope.network_create = {
            "name":network.name,
            "id":network.id
        };
        $scope.operation = 'edit';
        $modal.open({
            templateUrl: 'network_create.html',
            controller: 'NetworkCreateController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                network_table: function () {
                    return $scope.network_table;
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
                            "network_id":items_key[i]
                        }
                        CommonHttpService.post("/api/networks/delete/", post_data).then(function (data) {
                            if (data.OPERATION_STATUS == 1) {
                                $scope.network_table.reload();
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

    $scope.detach_action = function(network, action){
        bootbox.confirm($i18next("network.confirm_" + action), function (confirm) {
            if (confirm) {
                var post_data = {
                    "network_id":network.id,
                    "action":action
                }
                CommonHttpService.post("/api/networks/router/action", post_data).then(function (data) {
                    if (data.OPERATION_STATUS == 1) {
                        $scope.network_table.reload();
                    }
                    else {
                        ToastrService.error(data.MSG, $i18next("op_failed"));
                    }
                });
            }
        });
    }
    $scope.cidr = {
        "first":"172",
        "two":"31",
        "three":"0",
        "four":"0"
    }
    $scope.modal_attach_network = function(network){
        $scope.selectedNetwork=network;
        CommonHttpService.get("/api/routers/search/").then(function (data) {
            $scope.routers = data;
        });
        $modal.open({
            templateUrl: 'network_attach_router.html',
            controller: 'NetworkAttachController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                network_table: function () {
                    return $scope.network_table;
                }
            }
        });

    }

    $scope.modal_release_network = function(network){
        angular.forEach($scope.network_data, function (item) {
            if (item==network) {
                item.routerId="";
                item.router="";
                item.netAddress="";
            }
        });

        $scope.network_table.reload();
    }

});


CloudApp.controller('NetworkCreateController',
    function($rootScope, $scope, $filter, $i18next,$modalInstance,network_table,CommonHttpService,ToastrService) {
        $scope.has_error = false;
        $scope.cancel = function () {
            $modalInstance.dismiss();
        };
        $scope.submit_click = function(network_create){
            if(typeof(network_create.name)==='undefined' || network_create.name == ""){
                $scope.has_error = true;
                return false;
            }
            var post_data = {
                "id":$scope.network_create.id,
                "name":$scope.network_create.name
            }
            CommonHttpService.post("/api/networks/create/", post_data).then(function (data) {
                if (data.OPERATION_STATUS == 1) {
                    ToastrService.success(data.MSG, $i18next("success"));
                    network_table.reload();
                }
                else {
                    ToastrService.error(data.MSG, $i18next("op_failed"));
                }
                $modalInstance.dismiss();
            });
        }

    });

CloudApp.controller('NetworkAttachController',
    function($rootScope, $scope, $filter, $modalInstance,network_table,CommonHttpService,ToastrService,$i18next) {
        $scope.has_error = false;
        $scope.router_selected = false;
        $scope.cancel = function () {
            $modalInstance.dismiss();
        };
        $scope.$watch('cidr.three',function(value){
            var reg = /^(^[0-9]$)|(^[1-9]\d$)|(^1\d{2}$)|(^2[0-4]\d$)|(^25[0-5]$)$/g
            if($.trim($scope.cidr.three)==''){
                $scope.cidr.three = 0;
            }
            $scope.cidr.three = $scope.cidr.three.replace(/[^\d]/g,'');
            if($scope.cidr.three!=''){
                if($scope.cidr.three.match(reg)==null){
                    $scope.cidr.three = 0
                }
            }
        });


        $scope.submit_click = function(router_selected,action){
            var address = $scope.cidr.first+"."+$scope.cidr.two+"."+$scope.cidr.three+"."+$scope.cidr.four+"/24";
            if(!router_selected){
                $scope.has_error = true;
                return false;
            }
            var post_data={
                "router_id":router_selected.id,
                "network_id":$scope.selectedNetwork.id,
                "address":address,
                "action":action
            }
            CommonHttpService.post("/api/networks/router/action", post_data).then(function (data) {
                if (data.OPERATION_STATUS == 1) {
                    ToastrService.success(data.MSG, $i18next("success"));
                    network_table.reload();
                }
                else {
                    ToastrService.error(data.MSG, $i18next("op_failed"));
                }
                $modalInstance.dismiss();
            });
        }

    });




CloudApp.controller('NetworkTopologyController', function($rootScope, $scope,$i18next,$interval,CommonHttpService,ToastrService) {
    $scope.$on('$viewContentLoaded', function() {
        Metronic.initAjax();
    });

    $rootScope.settings.layout.pageBodySolid = true;
    $rootScope.settings.layout.pageSidebarClosed = false;


    CommonHttpService.get("/api/networks/topology").then(function (data) {
        horizon.network_topology.model = data;
        horizon.network_topology.init();
    });



});

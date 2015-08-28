'use strict';

CloudApp.controller('NetworkController',

    function($rootScope, $scope, $filter, $interval, $i18next, ngTableParams,
             $modal, CommonHttpService, ToastrService, ngTableHelper,
             Network, NetworkState) {

    $scope.$on('$viewContentLoaded', function() {   
        Metronic.initAjax();
    });

    $scope.current_network_data = [];
    $scope.network_table = new ngTableParams({
        page: 1,
        count: 10
    }, {
        counts: [],
        getData: function ($defer, params) {
            Network.query(function (data) {
                $scope.current_network_data = ngTableHelper.paginate(data, $defer, params)
                NetworkState.processList($scope.current_network_data);
            });
        }
    });

    //定时处理网络状态
    $rootScope.setInterval(function () {
        var list = $scope.current_network_data;
        var need_refresh = false;
        for (var i = 0; i < list.length; i++) {
            if (list[i].is_unstable) {
                need_refresh = true;
                break;
            }
        }
        if (need_refresh) {
            $scope.network_table.reload();
        }

    }, 5000);

    $scope.checkboxes = {'checked': false, items: {}};

    // watch for check all checkbox
    $scope.$watch('checkboxes.checked', function (value) {
        angular.forEach($scope.current_network_data, function (item) {
            if(item.is_stable){
                if (angular.isDefined(item.id)) {
                    $scope.checkboxes.items[item.id] = value;
                }
            }
        });
    });

    $scope.$watch('checkboxes.items', function (values) {
        $scope.checked_count = 0;
        if (!$scope.current_network_data) {
            return;
        }
        var checked = 0, unchecked = 0,
            total = $scope.current_network_data.length;

        angular.forEach($scope.current_network_data, function (item) {
            if(item.is_unstable){
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

    $scope.modal_create_network = function(){
        $scope.network_create = '';
        $scope.operation = 'create';
        $modal.open({
            templateUrl: 'network_create.html',
            controller: 'NetworkCreateController',
            backdrop: "static",
            scope: $scope
        }).result.then(function(){
            $scope.network_table.reload();
        });
    };

    $scope.modal_edit_network = function(network){

        $modal.open({
            templateUrl: 'edit_network.html',
            controller: 'NetworkEditController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                network: function(){
                    return angular.copy(network);
                }
            }
        }).result.then(function(){
            $scope.network_table.reload();
        });
    };

    $scope.batch_action = function(action){
        bootbox.confirm($i18next("network.confirm_" + action), function (confirm) {
            if (confirm) {
                var items = $scope.checkboxes.items;
                var items_key = Object.keys(items);
                for (var i = 0; i < items_key.length; i++) {
                    if (items[items_key[i]]) {
                        var post_data = {
                            "network_id":items_key[i]
                        };
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
    };

    //断开路由器连接
    $scope.detach = function(network){
        bootbox.confirm($i18next("network.confirm_detach"), function (confirm) {
            if (confirm) {

                var params = {"network_id": network.id};

                CommonHttpService.post("/api/networks/detach-router/", params).then(function (data) {
                    if (data.OPERATION_STATUS == 1) {
                        $scope.network_table.reload();
                        ToastrService.success(data.MSG, $i18next("success"));
                    } else {
                        ToastrService.error(data.MSG, $i18next("op_failed"));
                    }
                });
            }
        });
    };


    $scope.modal_attach_network = function(network){

        $modal.open({
            templateUrl: 'network_attach_router.html',
            controller: 'NetworkAttachController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                network_table: function () {
                    return $scope.network_table;
                },
                network: function(){
                    return angular.copy(network);
                },
                routers: function(){
                    return CommonHttpService.get("/api/routers/search/");
                }
            }
        });
    };
});


CloudApp.controller('NetworkCreateController',
    function($rootScope, $scope, $i18next, $modalInstance,
             CommonHttpService, ToastrService) {

        $scope.name_error = false;
        $scope.address_error=false;
        $scope.cancel =  $modalInstance.dismiss;
        $scope.network = {};
        $scope.cidr = {
            "first":"172",
            "two":"31",
            "three":"0",
            "four":"0"
        };

        $scope.$watch('cidr.three',function(value){
            var reg = /^(^[0-9]$)|(^[1-9]\d$)|(^1\d{2}$)|(^2[0-4]\d$)|(^25[0-5]$)$/g

            $scope.cidr.three = $scope.cidr.three.replace(/[^\d]/g,'');
            if($scope.cidr.three!=''){
                if($scope.cidr.three.match(reg)==null){
                    $scope.cidr.three = 0
                }
            }
        });

        $scope.save = function(network){

            $scope.name_error = !network.name;
            $scope.address_error = $.trim($scope.cidr.three)=='';

            if($scope.name_error || $scope.address_error){
                return;
            }

            var params = {
                "id": $scope.network.id,
                "name": $scope.network.name,
                "address": $scope.cidr.first+"."+$scope.cidr.two+"."+$scope.cidr.three+"."+$scope.cidr.four+"/24"
            };

            CommonHttpService.post("/api/networks/create/", params).then(function (data) {
                if (data.OPERATION_STATUS == 1) {
                    ToastrService.success(data.MSG, $i18next("success"));
                    $modalInstance.close();
                } else {
                    ToastrService.error(data.MSG, $i18next("op_failed"));
                }
            });
        }

    });


CloudApp.controller('NetworkEditController',
    function($rootScope, $scope, $i18next, $modalInstance,
             CommonHttpService, ToastrService, ValidationTool, network){

        var form = null;

        $scope.cancel = $modalInstance.dismiss;
        $scope.network = network;

        $modalInstance.rendered.then(function(){
            form = ValidationTool.init("#updateForm");
        });

        $scope.update = function(){

            if(form.valid() == false){
                return;
            }

            var params = {
                "id": network.id,
                "name": network.name
            };

            CommonHttpService.post("/api/networks/update/", params).then(function (data) {
                if (data.OPERATION_STATUS == 1) {
                    ToastrService.success(data.MSG, $i18next("success"));
                    $modalInstance.close();
                } else {
                    ToastrService.error(data.MSG, $i18next("op_failed"));
                }
            });
        }
    });

CloudApp.controller('NetworkAttachController',
    function($rootScope, $scope, $modalInstance, $i18next,
             CommonHttpService, ToastrService, ValidationTool,
             network_table, network, routers) {

        var form = null;

        $modalInstance.rendered.then(function(){
            form = $scope.form = ValidationTool.init('#attachRouterFrom');
        });

        $scope.network = network;
        $scope.routers = routers;
        $scope.cancel =  $modalInstance.dismiss;
        $scope.targetRouter = null;

        $scope.attach = function(){

            if(form.valid() == false){
                return;
            }

            var params = {
                "network_id":network.id,
                "router_id":$scope.targetRouter.id
            };

            CommonHttpService.post("/api/networks/attach-router/", params).then(function (data) {
                if (data.OPERATION_STATUS == 1) {
                    ToastrService.success(data.MSG, $i18next("success"));
                    network_table.reload();
                    $modalInstance.close();
                } else {
                    ToastrService.error(data.MSG, $i18next("op_failed"));
                }
            });
        };
    });

CloudApp.controller('NetworkTopologyController', function($rootScope, $scope,$i18next,$interval,CommonHttpService,ToastrService) {
    $scope.$on('$viewContentLoaded', function() {
        Metronic.initAjax();
    });

    CommonHttpService.get("/api/networks/topology").then(function (data) {
        horizon.network_topology.model = data;
        horizon.network_topology.init();
    });
});

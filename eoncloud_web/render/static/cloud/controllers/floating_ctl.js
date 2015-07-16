'use strict';

CloudApp.controller('FloatingController',
    function ($rootScope, $scope, $filter, $timeout, $interval, $modal, $i18next, ngTableParams, CommonHttpService, ToastrService, Instance, status_desc) {
        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });
        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;

        $scope.current_floating_data = [];
        $scope.status_desc = status_desc;
        $scope.selected_floatingIP = false;

        $scope.floating_table = new ngTableParams({
            page: 1,
            count: 10
        }, {
            counts: [],
            getData: function ($defer, params) {
                CommonHttpService.get("/api/floatings/").then(function (data) {
                    var data_list = params.sorting() ?
                        $filter('orderBy')(data, params.orderBy()) : name;
                    params.total(data_list.length);
                    $scope.current_floating_data = data_list.slice((params.page() - 1) * params.count(), params.page() * params.count());
                    $defer.resolve($scope.current_floating_data);
                });
            }
        });

        //定时处理硬盘状态

        var previous_refresh = false;
        var timer = $interval(function () {
            var list = $scope.current_floating_data;
            var need_refresh = false;
            for (var i = 0; i < list.length; i++) {
                if (status_desc[list[i].status][1] == 0) {
                    need_refresh = true;
                    break;
                }
            }
            if (need_refresh) {
                $scope.floating_table.reload();
                previous_refresh = true;
            } else {
                if (previous_refresh) {
                    $scope.floating_table.reload();
                }
                previous_refresh = false;
            }
        }, 5000);
        $rootScope.timer_list.push(timer);

        /////////////////////////
        $scope.checkboxes = {'checked': false, items: {}};

        // watch for check all checkbox
        $scope.$watch('checkboxes.checked', function (value) {
            angular.forEach($scope.current_floating_data, function (item) {
                if (angular.isDefined(item.id)) {
                    $scope.checkboxes.items[item.id] = value;
                }
            });
        });

        // watch for data checkboxes
        $scope.$watch('checkboxes.items', function (values) {
            $scope.checked_count = 0;
            if (!$scope.current_floating_data) {
                return;
            }
            var checked = 0, unchecked = 0,
                total = $scope.current_floating_data.length;

            angular.forEach($scope.current_floating_data, function (item) {
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

        $scope.modal_create_floating = function () {
            $modal.open({
                templateUrl: 'addFloating.html',
                controller: 'FloatCreateController',
                backdrop: "static",
                //size: 'lg',
                resolve: {
                    floating_table: function () {
                        return $scope.floating_table;
                    },
                    quota: function(CommonHttpService){
                        return CommonHttpService.get("/api/account/quota/");
                    }
                }
            });
        };

        $scope.modal_binding_instance = function (floating) {
            $modal.open({
                templateUrl: 'associate.html',
                controller: 'AssociateController',
                backdrop: "static",
                resolve: {
                    floating: function () {
                        return floating;
                    },
                    instances: function () {
                        return CommonHttpService.get("/api/floatings/target_list/");;
                    },
                    floating_table: function () {
                        return $scope.floating_table;
                    }
                }
            });
        };

        $scope.modal_change_bandwidth = function (float) {
            $scope.floatingIP = float;
            $modal.open({
                templateUrl: 'changeBandwidth.html',
                controller: 'changeBandwidthController',
                backdrop: "static",
                size: 'lg',
                scope: $scope,
                resolve: {
                    floating_table: function () {
                        return $scope.floating_table;
                    }
                }
            });

        }

        var post_action = function (floating, action) {
            bootbox.confirm($i18next("floatingIP.confirm_" + action), function (confirm) {
                if (confirm) {
                    var post_data = {
                        "floating_id": floating.id,
                        "action": action
                    }
                    CommonHttpService.post("/api/floatings/action/", post_data).then(function (data) {
                        if (data.OPERATION_STATUS == 1) {
                            ToastrService.success($i18next("op_success_msg"), $i18next("success"));
                            $scope.floating_table.reload();
                        }
                        else {
                            ToastrService.error($i18next("op_failed_msg"), $i18next("op_failed"));
                        }
                    });
                }
            });
        }

        var action_release = function (floating) {
            post_action(floating, "release");
        };
        var action_disassociate = function (floating) {
            post_action(floating, "disassociate");
        };

        $scope.floating_action = function (floating, action) {
            var action_func = {
                "release": action_release,
                "disassociate": action_disassociate
            };

            action_func[action](floating);
        };
    });

CloudApp.controller('FloatCreateController',
    function ($rootScope, $scope, $filter, $modalInstance, CommonHttpService, floating_table, $i18next, ToastrService, quota) {
        $scope.floatingIP = {
            "size": 5
        };
        $scope.quota = quota;
        //定义表单是否有错
        $scope.has_error = false;
        $scope.cancel = function () {
            $modalInstance.dismiss();
        };

        $scope.calcuate_resource_persent = function (resource) {
            if (quota[resource] <= 0) {
                return 0;
            }
            else {
                return (quota[resource + "_used"] + 1 ) / quota[resource] * 100;

            }
        };
        $scope.resource_persent = function(resource){
            return $scope.calcuate_resource_persent(resource) + "%";
        }

        $scope.check_can_submit = function(){
            if(quota.floating_ip <= 0){
                return false;
            }
            else{
                return quota.floating_ip_used + 1 > quota.floating_ip;
            }
        };
        $scope.create = function (floating) {
            if (typeof(floating.size) === 'undefined' || floating.size == "") {
                $scope.has_error = true;
                return false;
            }

            var post_data = {"bandwidth": floating.size};
            CommonHttpService.post("/api/floatings/create/", post_data).then(function (data) {
                if (data.OPERATION_STATUS == 1) {
                    ToastrService.success($i18next("floatingIP.create_success_and_waiting"), $i18next("success"));
                    floating_table.reload();
                }
                else {
                    ToastrService.error($i18next("op_failed_msg"), $i18next("op_failed"));
                }
                $modalInstance.dismiss();
            });
        }
    });

CloudApp.controller('AssociateController',
    function ($rootScope, $scope, $filter, $modalInstance, $i18next, ToastrService, CommonHttpService, floating_table, floating, instances) {
        $scope.cancelBinding = function () {
            $modalInstance.dismiss();
        };

        $scope.floating = floating;
        $scope.instances = instances;
        $scope.selected_instance = false;
        $scope.has_error = false;


        $scope.associate = function () {
            if (!$scope.selected_instance) {
                $scope.has_error = true;
                return;
            }

            var post_data = {
                "action": "associate",
                "floating_id": $scope.floating.id,
                "resource": $scope.selected_instance.id,
                "resource_type":$scope.selected_instance.resource_type
            }
            CommonHttpService.post("/api/floatings/action/", post_data).then(function (data) {
                if (data.OPERATION_STATUS == 1) {
                    ToastrService.success($i18next("floatingIP.op_success_and_waiting"), $i18next("success"));
                    floating_table.reload();
                }
                else {
                    ToastrService.error($i18next("op_failed_msg"), $i18next("op_failed"));
                }
                $modalInstance.dismiss();
            });
        };

        $scope.$watch("selected_instance", function (value) {
            if (value) {
                $scope.has_error = false;
            }
        });
    });
CloudApp.controller('changeBandwidthController',
    function ($rootScope, $scope, $filter, $modalInstance, floating_table) {
        $scope.cancel = function () {
            $modalInstance.dismiss();
        };

        $scope.create = function () {

            $modalInstance.dismiss();
            floating_table.reload();
        }

    });

CloudApp.directive("floatslider", [function () {
    return {
        restrict: 'E',
        templateUrl: 'slider.html',
        scope: {
            data: "=data"
        },
        link: function (scope, el, attrs, ctrl) {
            $(el).find("#slider-range-max").slider({
                isRTL: false,
                range: "max",
                min: 1,
                step: 1,
                max: 30,
                value: 5,
                slide: function (event, ui) {
                    scope.data.size = ui.value;
                    scope.$apply();
                }
            });
        }
    };
}]);

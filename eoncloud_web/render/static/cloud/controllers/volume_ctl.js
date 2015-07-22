'use strict';

CloudApp.controller('VolumeController', function ($rootScope, $scope, $filter, $interval, $modal, $i18next, $timeout, ngTableParams, status_desc, Volume, Instance, CommonHttpService, ToastrService) {
    $scope.$on('$viewContentLoaded', function () {
        Metronic.initAjax();
    });

    $rootScope.settings.layout.pageBodySolid = true;
    $rootScope.settings.layout.pageSidebarClosed = false;

    $scope.status_desc = status_desc;
    $scope.current_volume_data = [];

    $scope.volume_table = new ngTableParams({
        page: 1,
        count: 10
    }, {
        counts: [],
        getData: function ($defer, params) {
            Volume.query(function (data) {
                var data_list = params.sorting() ?
                    $filter('orderBy')(data, params.orderBy()) : data;
                params.total(data_list.length);
                $scope.current_volume_data = data_list.slice((params.page() - 1) * params.count(), params.page() * params.count());
                $defer.resolve($scope.current_volume_data);
            });
        }
    });
    //定时处理硬盘状态
    var timer = $interval(function () {
        var list = $scope.current_volume_data;
        var need_refresh = false;
        for (var i = 0; i < list.length; i++) {
            if (status_desc[list[i].status][1] == 0) {
                need_refresh = true;
                break;
            }
        }
        if (need_refresh) {
            $scope.volume_table.reload();
        }

    }, 5000);
    $rootScope.timer_list.push(timer);
    /////////////////////////
    $scope.checkboxes = {'checked': false, items: {}};

    // watch for check all checkbox
    $scope.$watch('checkboxes.checked', function (value) {
        angular.forEach($scope.current_volume_data, function (item) {
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
        if (!$scope.current_volume_data) {
            return;
        }
        var checked = 0, unchecked = 0,
            total = $scope.current_volume_data.length;

        angular.forEach($scope.current_volume_data, function (item) {
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

    /*创建云硬盘弹出窗口*/
    $scope.modal_create_volume = function () {
        //云硬盘元数据定义
        $scope.volume = {
            "count": 1,
            "size": 10
        };
        var modalVolume = $modal.open({
            templateUrl: 'create_volume.html',
            controller: 'VolumeCreateController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                volume_table: function () {
                    return $scope.volume_table;
                },
                quota: function (CommonHttpService) {
                    return CommonHttpService.get("/api/account/quota/");
                }
            }
        });
        modalVolume.result.then(function (result) {
        }, function (result) {
        });
    }
    /*修改云硬盘弹出窗口*/
    $scope.modal_update_volume = function (volume) {
        $scope.volume = {
            "id": volume.id,
            "name": volume.name
        };
        console.log($scope.volume)
        var modalVolume = $modal.open({
            templateUrl: 'update_volume.html',
            controller: 'VolumeCreateController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                volume_table: function () {
                    return $scope.volume_table;
                },
                quota: function (CommonHttpService) {
                    return CommonHttpService.get("/api/account/quota/");
                }
            }
        });
        modalVolume.result.then(function (result) {
        }, function (result) {
        });
    }
    /*挂载云硬盘弹出窗口*/
    $scope.modal_attach_to_instance = function (volume) {
        CommonHttpService.get("/api/instances/search/").then(function (data) {
            $scope.instances = data;
        });
        $scope.volume = volume;
        var modalVolume = $modal.open({
            templateUrl: 'instance.html',
            controller: 'VolumeAttachController',
            backdrop: "static",
            scope: $scope,
            resolve: {

                operation_tip: function () {
                    return "";
                },
                volume_table: function () {
                    return $scope.volume_table;
                }
            }
        });
        modalVolume.result.then(function (result) {
        }, function (result) {
        });
    }
    /*卸载云硬盘弹出窗口*/
    $scope.modal_detach_from_instance = function (volume) {
        $scope.volume = volume;
        var modalVolume = $modal.open({
            templateUrl: 'detach.html',
            controller: 'VolumeAttachController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                operation_tip: function () {
                    return $i18next("volume.detach_tip_start") + volume.instance_info.name + $i18next("volume.detach_tip_end");
                },
                instances: function () {
                    return "";
                },
                volume_table: function () {
                    return $scope.volume_table;
                }
            }
        });
        modalVolume.result.then(function (result) {
        }, function (result) {
        });
    };
    var post_action = function (vol, action) {
        var post_data = {
            "action": action,
            "volume_id": vol.id
        };
        CommonHttpService.post("/api/volumes/action/", post_data).then(function (data) {
            if (data.OPERATION_STATUS == 1) {
                $scope.volume_table.reload();
            }
            else {
                ToastrService.error(data.MSG, $i18next("op_failed"));
            }
        });
    };
    //批量操作 delete
    $scope.batch_action = function (action) {
        bootbox.confirm($i18next("volume.confirm_" + action), function (confirm) {
            if (confirm) {
                var items = $scope.checkboxes.items;
                var items_key = Object.keys(items);
                for (var i = 0; i < items_key.length; i++) {
                    if (items[items_key[i]]) {
                        post_action({"id": items_key[i]}, action);
                        $scope.checkboxes.items[items_key[i]] = false;
                    }
                }
            }
        });
    }
});
/*云硬盘创建类*/
CloudApp.controller('VolumeCreateController',
    function ($rootScope, $scope, $sce, $modalInstance, $i18next, CommonHttpService, ToastrService, volume_table, quota) {
        $scope.quota = quota;

        $scope.calcuate_resource_persent = function (resource) {
            if (quota[resource] <= 0) {
                return 0;
            }
            else {
                if(resource == "volume")
                    return (quota[resource + "_used"] + 1 ) / quota[resource] * 100;

                if(resource == "volume_size")
                    return (quota[resource + "_used"] + $scope.volume.size ) / quota[resource] * 100;

            }
        };
        $scope.resource_persent = function(resource){
            return $scope.calcuate_resource_persent(resource) + "%";
        }

        $scope.check_can_submit = function(){
            if(quota.volume <= 0 && quota.volume_size <= 0){
                return false;
            }
            else{
                var quota_volume_overlimt = false;
                var quota_volume_size_overlimt = false;

                if(quota.volume > 0)
                    quota_volume_overlimt = quota.volume_used + 1 > quota.volume;

                if(quota.volume_size > 0)
                    quota_volume_size_overlimt = quota.volume_size_used + $scope.volume.size > quota.volume_size;

                return quota_volume_overlimt || quota_volume_size_overlimt;
            }
        };
        //定义表单是否有错
        $scope.has_error = false;
        //监听model变化情况
        $scope.$watch('volume.name', function () {
            $scope.has_error = false;
        });
        //关闭窗口方法
        $scope.cancel = function () {
            $modalInstance.dismiss();
        };
        //控制表单重复提交
        $scope.flag = true;
        //提交方法
        $scope.volume_submit = function (volume, type) {
            if (typeof(volume.name) === 'undefined' || volume.name == "") {
                $scope.has_error = true;
                return false;
            }
            if(!$scope.flag){
                return
            }
            $scope.flag = false;
            if ("create" === type) {
                var post_data = {
                    "name": volume.name,
                    "size": volume.size
                }
                CommonHttpService.post("/api/volumes/create/", post_data).then(function (data) {
                    if (data.OPERATION_STATUS == 1) {
                        ToastrService.success(data.MSG, $i18next("success"));
                    }
                    else {
                        ToastrService.error(data.MSG, $i18next("op_failed"));
                    }
                    volume_table.reload();
                    $modalInstance.dismiss();
                });
            } else if ("update" === type) {

                var post_data = {
                    "id": volume.id,
                    "name": volume.name
                }
                CommonHttpService.post("/api/volumes/update/", post_data).then(function (data) {
                    if (data.OPERATION_STATUS == 1) {
                        ToastrService.success(data.MSG, $i18next("success"));
                    }
                    else {
                        ToastrService.error(data.MSG, $i18next("op_failed"));
                    }
                    volume_table.reload();
                    $modalInstance.dismiss();
                });
            }
        }
    });
/*云硬盘挂载controller*/
CloudApp.controller('VolumeAttachController', function ($rootScope, $scope, $sce, $modalInstance, $i18next, CommonHttpService, ToastrService, operation_tip, volume_table) {
    //定义表单是否有错
    $scope.has_error = false;
    $scope.selected_instance = false;
    //卸载云主机提示 卸载操作使用
    $scope.operation_tip = operation_tip;

    //关闭窗口方法
    $scope.cancel = function () {
        $modalInstance.dismiss();
    };
    $scope.flag = true;
    //挂载方法
    $scope.attach_or_detach = function (selected_instance, action) {
        if ((action == "attach" && selected_instance) || action=='detach') {
            if(!$scope.flag){
                return
            }
            $scope.flag = false;
            var post_data = {
                "volume_id": $scope.volume.id,
                "instance_id": selected_instance.id,
                "action": action
            }
            CommonHttpService.post("/api/volumes/action/", post_data).then(function (data) {
                if (data.OPERATION_STATUS == 1) {
                    ToastrService.success(data.MSG, $i18next("success"));
                    volume_table.reload();
                }
                else {
                    ToastrService.error(data.MSG, $i18next("op_failed"));
                }
                $modalInstance.dismiss();
            });
        } else {
            $scope.has_error = true;
        }

    };

});


CloudApp.directive("slider", [function () {
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
                min: 10,
                step: 10,
                max: 1000,
                value: 1,
                slide: function (event, ui) {
                    scope.data.size = ui.value;
                    scope.$apply();
                }
            });
        }
    };
}]);

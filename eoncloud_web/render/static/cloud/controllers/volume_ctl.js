'use strict';

angular.module("CloudApp")
    .controller('VolumeController',
        function($rootScope, $scope, $filter, $interval,
                 $modal, $i18next, $timeout, $ngBootbox,
                 ngTableParams, CommonHttpService, ToastrService, lodash,
                 ngTableHelper, VolumeState, Volume){

            $scope.$on('$viewContentLoaded', function () {
                Metronic.initAjax();
            });

            $scope.current_volume_data = [];

            $scope.volume_table = new ngTableParams({
                page: 1,
                count: 10
            }, {
                counts: [],
                getData: function ($defer, params) {
                    Volume.query(function (data) {
                        $scope.current_volume_data = ngTableHelper.paginate(data, $defer, params);
                        VolumeState.processList($scope.current_volume_data);
                    });
                }
            });

            //定时处理硬盘状态
             $rootScope.setInterval(function () {
                if (lodash.any($scope.current_volume_data, 'isUnstable')) {
                    $scope.volume_table.reload();
                }
            }, 5000);

            $scope.checkboxes = {'checked': false, items: {}};

            // watch for check all checkbox
            $scope.$watch('checkboxes.checked', function (value) {
                angular.forEach($scope.current_volume_data, function (item) {
                    if (item.isStable && angular.isDefined(item.id)) {
                        $scope.checkboxes.items[item.id] = value;
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

                angular.forEach($scope.current_volume_data, function (volume) {
                    if(volume.isUnstable){
                        $scope.checkboxes.items[volume.id] = false;
                    }
                    checked += ($scope.checkboxes.items[volume.id]) || 0;
                    unchecked += (!$scope.checkboxes.items[volume.id]) || 0;
                });
                if ((unchecked == 0) || (checked == 0)) {
                    $scope.checkboxes.checked = ((checked == total) && total != 0);
                }

                $scope.checked_count = checked;
                // grayed checkbox
                angular.element(document.getElementById("select_all")).prop("indeterminate", (checked != 0 && unchecked != 0));
            }, true);

            /*创建云硬盘弹出窗口*/
            $scope.modal_create_volume = function () {
                //云硬盘元数据定义
                $scope.volume = {
                    "count": 1,
                    "size": 10
                };

                $modal.open({
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
            };

            /*修改云硬盘弹出窗口*/
            $scope.modal_update_volume = function (volume) {
                $scope.volume = {
                    "id": volume.id,
                    "name": volume.name
                };
                $modal.open({
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
            };

            /*挂载云硬盘弹出窗口*/
            $scope.openAttachModal = function(volume){

                CommonHttpService.get("/api/instances/search/").then(function (data) {
                    $scope.instances = data;
                });

                $modal.open({
                    templateUrl: 'attach.html',
                    controller: 'VolumeAttachController',
                    backdrop: "static",
                    scope: $scope,
                    resolve: {
                        volume: function(){
                            return volume;
                        }
                    }
                }).result.then(function(){
                    $scope.volume_table.reload();
                });
            };

            $scope.detach = function (volume) {

                $ngBootbox.confirm($i18next("volume.detach_confirm",
                        {instance: volume.instance_info.name})).then(function(){

                    var post_data = {
                        "volume_id": volume.id,
                        "action": 'detach'
                    };

                    CommonHttpService.post("/api/volumes/action/", post_data).then(function (data) {
                        if (data.success) {
                            ToastrService.success(data.msg, $i18next("success"));
                            $scope.volume_table.reload();
                        } else {
                            ToastrService.error(data.msg, $i18next("op_failed"));
                        }
                    });
                });
            };

            var deleteVolume= function (volumeId) {

                var params = {"volume_id": volumeId, 'action': 'delete'};

                CommonHttpService.post("/api/volumes/action/", params).then(function (data) {
                    if (data.success) {
                        $scope.volume_table.reload();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            };

            var deleteVolumes = function(ids){

                $ngBootbox.confirm($i18next("volume.confirm_delete")).then(function(){

                    if(typeof ids == 'function'){
                        ids = ids();
                    }

                    for (var i = 0; i < ids.length; i++) {
                        deleteVolume(ids[i]);
                    }
                });
            };

            $scope.batchDelete = function(){

                deleteVolumes(function(){
                    var items = $scope.checkboxes.items;
                    var items_key = Object.keys(items);

                    var ids = [];
                    for (var i = 0; i < items_key.length; i++) {
                        if (items[items_key[i]]) {
                            ids.push(items_key[i]);
                            $scope.checkboxes.items[items_key[i]] = false;
                        }
                    }

                    return ids;
                });
            };

            $scope.delete = function(volume){
                deleteVolumes([volume.id]);
            };
        })

    .controller('VolumeCreateController',
        function ($rootScope, $scope, $modalInstance,
                  $i18next, CommonHttpService, ToastrService,
                  volume_table, quota){

            $scope.quota = quota;

            var calcuate_resource_persent = function (resource) {
                if (quota[resource] <= 0) {
                    return 0;
                } else {
                    if(resource == "volume"){
                        return (quota[resource + "_used"] + 1 ) / quota[resource] * 100;
                    }

                    if(resource == "volume_size"){
                        return (quota[resource + "_used"] + $scope.volume.size ) / quota[resource] * 100;
                    }
                }
            };

            $scope.isExhausted = function(resource){
                return calcuate_resource_persent(resource) > 100;
            };

            $scope.usageRatio = function(resource){
                return calcuate_resource_persent(resource) + "%";
            };

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
                        if (data.success) {
                            ToastrService.success(data.msg, $i18next("success"));
                        } else {
                            ToastrService.error(data.msg, $i18next("op_failed"));
                        }
                        volume_table.reload();
                        $modalInstance.dismiss();
                    });
                } else if ("update" === type) {

                    var post_data = {
                        "id": volume.id,
                        "name": volume.name
                    };

                    CommonHttpService.post("/api/volumes/update/", post_data).then(function (data) {
                        if (data.success) {
                            ToastrService.success(data.msg, $i18next("success"));
                        }
                        else {
                            ToastrService.error(data.msg, $i18next("op_failed"));
                        }
                        volume_table.reload();
                        $modalInstance.dismiss();
                    });
                }
            }
        }
    )
    .controller('VolumeAttachController',
        function ($rootScope, $scope, $modalInstance,  $i18next,
                  CommonHttpService, ToastrService, volume) {

            $scope.volume = volume;
            $scope.target_instance = null;
            $scope.cancel =  $modalInstance.dismiss;
            $scope.has_error = false;

            $scope.attach = function (){

                $scope.has_error = $scope.target_instance == null;

                if($scope.has_error){
                    return;
                }

                var post_data = {
                    "volume_id": volume.id,
                    "instance_id": $scope.target_instance.id,
                    "action": 'attach'
                };

                CommonHttpService.post("/api/volumes/action/", post_data).then(function (data) {
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $modalInstance.close();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            }
        }
    )

    .directive("slider", [function () {
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

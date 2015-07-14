'use strict';

CloudApp.controller('BackupController',
    function ($rootScope, $scope, $filter, $timeout, $i18next, $modal, $interval,
              ToastrService, ngTableParams, CommonHttpService, Backup, status_desc) {
        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;

        $scope.status_desc = status_desc;

        $scope.backup_table = new ngTableParams({
            page: 1,
            count: 10
        }, {
            counts: [],
            getData: function ($defer, params) {
                Backup.query(function (data) {
                    var data_list = params.sorting() ?
                        $filter('orderBy')(data, params.orderBy()) : data;
                    params.total(data_list.length);
                    $scope.current_backup_data = data_list.slice((params.page() - 1) * params.count(), params.page() * params.count());
                    $defer.resolve($scope.current_backup_data);
                });
            }
        });

        var previous_refresh = false;
        var timer = $interval(function () {
            var list = $scope.current_backup_data;
            var need_refresh = false;
            for (var i = 0; i < list.length; i++) {
                if (status_desc[list[i].status][1] == 0) {
                    need_refresh = true;
                    break;
                }
            }
            if (need_refresh) {
                $scope.backup_table.reload();
                previous_refresh = true;
            }
            else {
                if (previous_refresh) {
                    $scope.backup_table.reload();
                }
                previous_refresh = false;
            }

        }, 5000);

        $rootScope.executeWhenLeave(function(){
            $interval.cancel(timer);
        });


        $scope.instance_backup = function (backup) {
            if (backup.instance) {
                return true;
            }
            else {
                return false;
            }
        };

        var func_detail = function (backup) {
            $scope.modalInstance = $modal.open({
                templateUrl: 'detail.html',
                controller: 'BackupDetailController',
                backdrop: "static",
                size: 'lg',
                scope: $scope,
                resolve: {
                    'status_desc': function () {
                        return status_desc;
                    },
                    'backup_info': function () {
                        return backup;
                    }
                }
            });
        };

        var post_func = function (backup, post_data) {
            CommonHttpService.post("/api/backup/action/", post_data).then(function (data) {
                if (data.OPERATION_STATUS == 1) {
                    $scope.modalInstance.dismiss();
                    $scope.backup_table.reload();
                }
                else if (data.OPERATION_STATUS == 2) {
                    ToastrService.warning($i18next("op_forbid_msg"), $i18next("op_failed"));
                    $scope.modalInstance.dismiss();
                }
                else {
                    ToastrService.error($i18next("op_failed_msg"), $i18next("op_failed"));
                }
            });
        };

        var func_delete = function (backup) {
            bootbox.confirm($i18next("backup.confirm_delete"), function (confirm) {
                if (confirm) {
                    var post_data = {
                        "pk": backup.id,
                        "action": "delete"
                    }
                    post_func(backup, post_data);
                }
            });
        };
        var func_restore = function (backup, item) {
            bootbox.confirm($i18next("backup.confirm_restore"), function (confirm) {
                if (confirm) {
                    var post_data = {
                        "pk": backup.id,
                        "action": "restore",
                        "item_id": item ? item.id : ''
                    };

                    post_func(backup, post_data);
                }
            });
        };

        var func = {
            "detail": func_detail,
            "delete": func_delete,
            "restore": func_restore
        };

        $scope.backup_action = function (backup, action, item) {
            func[action](backup, item);
        }
    });

CloudApp.controller("BackupDetailController",
    function ($rootScope, $scope, $filter, $timeout, $i18next, $modalInstance, ngTableParams, CommonHttpService, Backup, status_desc, backup_info) {
        $scope.backup_info = backup_info;
        $scope.status_desc = status_desc;
        $scope.cancel = function () {
            $modalInstance.dismiss();
        };

        $scope.backup_table = new ngTableParams({
            page: 1,
            count: 10
        }, {
            counts: [],
            getData: function ($defer, params) {
                var data_list = backup_info.items;
                params.total(data_list.length);
                $scope.current_backup_data = data_list.slice((params.page() - 1) * params.count(), params.page() * params.count());
                $defer.resolve($scope.current_backup_data);

            }
        });
    });

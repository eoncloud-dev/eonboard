/**
 * Created with PyCharm.
 * User: bluven
 * Date: 15-6-29
 * Time: 下午2:11
 * To change this template use File | Settings | File Templates.
 **/

CloudApp.controller('DataCenterController',
    function($rootScope, $scope, $filter, $modal, $i18next,
             CommonHttpService, ToastrService, ngTableParams, DataCenter){

        $scope.$on('$viewContentLoaded', function(){
                Metronic.initAjax();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;

        $scope.checkAllFlag = false;

        $scope.data_centers = [];

        $scope.toggleAll = function(){
            $scope.checkAllFlag = !$scope.checkAllFlag;

            angular.forEach($scope.data_centers, function(data_center){
                data_center.checked = $scope.checkAllFlag;
            });
        };

        $scope.not_checked = function(){

            var count = 0;

            angular.forEach($scope.data_centers, function(data_center){

                if(data_center.checked){
                    count += 1;
                }
            });

            return count == 0;
        };


        $scope.data_center_table = new ngTableParams({
                page: 1,
                count: 10
            },{
                counts: [],
                getData: function ($defer, params) {
                    DataCenter.query(function (data) {

                        var results = $filter('orderBy')(data, params.orderBy());

                        params.total(results.length);

                        $scope.data_centers = results.slice((params.page() - 1) * params.count(), params.page() * params.count());

                        $defer.resolve($scope.data_centers);
                    });
                }
            });

        $scope.create = function(data_center) {

                data_center = data_center || {};

                $modal.open({
                    templateUrl: 'create.html',
                    controller: 'DataCenterCreateController',
                    backdrop: "static",
                    size: 'lg',
                    resolve: {
                        data_center_table: function () {
                            return $scope.data_center_table;
                        },
                        data_center: function(){return data_center;}
                    }
                });
            };

        $scope.edit = $scope.create;

        var batchDelete = function(ids){

            CommonHttpService.post("/api/data-centers/batch-delete/", {ids: ids}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.data_center_table.reload();
                        $scope.checkAllFlag = false;
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
        };

        $scope.batch_delete = function(){

            bootbox.confirm($i18next("data_center.confirm_delete"), function (confirmed) {

                if(!confirmed){
                    return;
                }

                var ids = [];

                angular.forEach($scope.data_centers, function(data_center){

                    if(data_center.checked){
                        ids.push(data_center.id);
                    }
                });

                batchDelete(ids);
            });
        };

        $scope.delete = function(data_center){

            bootbox.confirm($i18next("data_center.confirm_delete"), function (confirmed) {

                if(!confirmed){
                    return;
                }

                batchDelete([data_center.id]);
            });
        };
    })
    .controller('DataCenterCreateController',
        function($rootScope, $scope, $modalInstance,
                 data_center_table, data_center, DataCenterForm,
                 $i18next, CommonHttpService, ToastrService){

            $scope.data_center = data_center;

            $modalInstance.opened.then(function() {
                setTimeout(DataCenterForm.init, 0)
            });

            $scope.cancel = function () {
                $modalInstance.dismiss();
            };

            $scope.submit = function(data_center){

                if(!$("#dataCenterForm").validate().form()){
                    return;
                }

                data_center = angular.copy(data_center);

                var url = '/api/data-centers';

                if(data_center.id){
                    url += "/update/";
                } else {
                    url += "/create/";
                }

                CommonHttpService.post(url, data_center).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        data_center_table.reload();
                        $modalInstance.dismiss();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            };
        }
    ).factory('DataCenterForm', ['ValidationTool', function(ValidationTool) {
        return {
            init: function(){

                jQuery.validator.addMethod('ip', function(value, element){
                    return /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(value);
                }, '请输入正确的IP地址');

                var config = {
                    rules: {
                        name: {
                            minlength: 2,
                            maxlength: 128,
                            required: true
                        },
                        host: {
                            required: true,
                            ip: true
                        },
                        project: {
                            required: true,
                            minlength: 2,
                            maxlength: 128
                        },
                        user: {
                            required: true,
                            minlength: 2,
                            maxlength: 128
                        },
                        password: {
                            required: true,
                            minlength: 2,
                            maxlength: 50
                        },
                        auth_url: {
                            required: true,
                            url: true
                        },
                        ext_net: {
                            required: true,
                            minlength: 2,
                            maxlength: 128
                        }
                    }};

                console.log('validation tool');
                ValidationTool.init('#dataCenterForm', config);
              }
            }
        }]
    );

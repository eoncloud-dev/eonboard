/**
 * User: bluven
 * Date: 15-6-25
 */


'use strict';

CloudApp.controller('ContractController',
    function ($rootScope, $scope, $filter,
              $modal, $i18next, ngTableParams, Contract,
              CommonHttpService, ToastrService,
              ngTableHelper) {

        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        $scope.contracts = [];

        $scope.contract_table = new ngTableParams({
            page: 1,
            count: 10
        },{
            counts: [],
            getData: function ($defer, params) {

                var searchParams = {page: params.page(), page_size: params.count()};
                Contract.query(searchParams, function (data) {
                    $defer.resolve(data.results);
                    $scope.contracts = data.results;
                    ngTableHelper.countPages(params, data.count);
                });
            }
        });

        $scope.create = function() {
            $modal.open({
                templateUrl: 'create.html',
                controller: 'ContractCreateController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    contract_table: function () {
                        return $scope.contract_table;
                    }
                }
            });
        };

        $scope.edit = function(contract){

            $modal.open({
                templateUrl: 'update.html',
                controller: 'ContractUpdateController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    contract_table: function () {
                        return $scope.contract_table;
                    },
                    contract: function(){return contract}
                }
            });
        };

        $scope.manage_quota = function(contract){
            $modal.open({
                templateUrl: 'manage-quota.html',
                controller: 'ManageQuotaController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    contract: function(){return contract},
                    resource_options: function(CommonHttpService){
                        return CommonHttpService.get("/api/quota-resource-options");
                    }
                }
            });
        };
    })
    .controller('ContractCreateController',
        function($rootScope, $scope, $modalInstance, $i18next, contract_table,
                 User, Contract, UserDataCenter, ContractForm,
                 CommonHttpService, ToastrService, ResourceTool){

            var contract = $scope.contract = {};
            $scope.users = [];
            $scope.udcList = [];

            $modalInstance.rendered.then(ContractForm.init);

            $scope.cancel = $modalInstance.dismiss;

            $scope.users = User.getActiveUsers();
            $scope.loadUdcList = function(){
                UserDataCenter.query({user: contract.user}, function(udcList){
                    $scope.udcList = udcList;
                });
            };

            $scope.submit = function(contract){

                if(!$("#contractForm").validate().form()){
                    return;
                }

                contract = ResourceTool.copy_only_data(contract);

                contract.start_date += " 00:00:00";
                contract.end_date += " 23:59:00";

                CommonHttpService.post("/api/contracts/create", contract).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        contract_table.reload();
                        $modalInstance.close();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            };
        }
    ).controller('ContractUpdateController',
        function($rootScope, $scope, $modalInstance, $i18next,
                 contract, contract_table,
                 User, Contract, UserDataCenter, ContractForm,
                 CommonHttpService, ToastrService, ResourceTool){

            $scope.contract = contract = angular.copy(contract);
            $scope.user = {};
            $scope.udc = {};

            $modalInstance.rendered.then(ContractForm.init);

            $scope.cancel = function () {
                $modalInstance.dismiss();
            };

            User.get({id: contract.user}, function(user){
                $scope.user = user;
            });

            UserDataCenter.get({id: contract.udc}, function(udc){
                $scope.udc = udc;
            });

            $scope.submit = function(contract){

                if(!$("#contractForm").validate().form()){
                    return;
                }

                contract = ResourceTool.copy_only_data(contract);

                contract.start_date += " 00:00:00";
                contract.end_date += " 23:59:00";

                CommonHttpService.post("/api/contracts/update/", contract).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        contract_table.reload();
                        $modalInstance.dismiss();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            };
        }
    ).factory('ContractForm', ['ValidationTool', 'DatePicker', function (ValidationTool, DatePicker) {
        return {
            init: function(){

                var config = {
                    rules: {
                        name: {
                            minlength: 6,
                            maxlength: 64,
                            required: true
                        },
                        customer: {
                            minlength: 2,
                            maxlength: 64,
                            required: true
                        },
                        user: 'required',
                        udc: 'required',
                        start_date: 'required',
                        end_date: 'required'
                    }
                };

                ValidationTool.init('#contractForm', config);
                DatePicker.initDatePickers();
              }
            }
        }]
    ).controller("ManageQuotaController", function(
        $rootScope, $scope, $modalInstance, $i18next,
        contract, resource_options, Quota, QuotaValidation,
        CommonHttpService, ToastrService){

         Quota.query({contract_id: contract.id}, function(quotas){

            var quotaMap = {};
            $scope.quotas = [];

            angular.forEach(quotas, function(quota){
                quotaMap[quota.resource] = quota;
            });

            angular.forEach(resource_options, function(option){

                var quota = quotaMap[option[0]] || {limit: 0};
                quota.resource = option[0];
                quota.resource_label = option[1];

                $scope.quotas.push(quota);

            });

        });

        $modalInstance.rendered.then(function() {
            $scope.form = QuotaValidation.init();
        });

        $scope.cancel = function () {
            $modalInstance.dismiss();
        };

        $scope.submit = function(){

            if(!$scope.form.valid()){
                return;
            }

            var params = {
                contract_id: contract.id,
                ids: [],
                resources: [],
                limits: []
            };

            angular.forEach($scope.quotas, function(quota){
                params.ids.push(quota.id);
                params.resources.push(quota.resource);
                params.limits.push(quota.limit);
            });

            CommonHttpService.post("/api/quotas/batch-create/", params).then(function(data){
                if (data.success) {
                    ToastrService.success(data.msg, $i18next("success"));
                    $modalInstance.dismiss();
                } else {
                    ToastrService.error(data.msg, $i18next("op_failed"));
                }
            });
        };


    }).factory('QuotaValidation', ['ValidationTool', function(ValidationTool){
        return {
            init: function(){
                return ValidationTool.init('#quotaForm', {});
            }
        }
    }]);
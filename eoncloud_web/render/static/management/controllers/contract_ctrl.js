/**
 * User: bluven
 * Date: 15-6-25
 */


'use strict';

CloudApp.controller('ContractController',
    function ($rootScope, $scope, $filter, $timeout,
              $modal, $i18next, ngTableParams, Contract,
              CommonHttpService, ToastrService) {

        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;

        $scope.checkAllFlag = false;
        $scope.contracts = [];

        $scope.toggleAll = function(){
            $scope.checkAllFlag = !$scope.checkAllFlag;

            angular.forEach($scope.contracts, function(contract){
                contract.deleted = $scope.checkAllFlag;
            });
        };

        $scope.not_checked = function(){

            var count = 0;

            angular.forEach($scope.contracts, function(contract){

                if(contract.deleted){
                    count += 1;
                }
            });

            return count == 0;
        };

        $scope.contract_table = new ngTableParams({
            page: 1,
            count: 10
        },{
            counts: [],
            getData: function ($defer, params) {
                Contract.query(function (data) {

                    var data_list = $filter('orderBy')(data, params.orderBy());

                    params.total(data_list.length);

                    $scope.contracts = data_list.slice((params.page() - 1) * params.count(), params.page() * params.count());

                    $defer.resolve($scope.contracts);
                });
            }
        });

        $scope.create = function() {
            $modal.open({
//                templateUrl: '/static/management/views/contract_create.html',
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

        var deleteContracts = function(contractIds){

            CommonHttpService.post("/api/contracts/batch-delete/", {contract_ids: contractIds}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.contract_table.reload();
                        $scope.checkAllFlag = false;
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
        };

        $scope.batch_delete = function(){

            bootbox.confirm($i18next("contract.confirm_delete"), function (confirmed) {

                if(!confirmed){
                    return;
                }

                var contractIds = [];

                angular.forEach($scope.contracts, function(contract){

                    if(contract.deleted){
                        contractIds.push(contract.id);
                    }
                });

                deleteContracts(contractIds);
            });
        };

        $scope.delete= function(contract){

            bootbox.confirm($i18next("contract.confirm_delete"), function (confirmed) {

                if(!confirmed){
                    return;
                }

                deleteContracts([contract.id]);
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

            $modalInstance.opened.then(function() {
                setTimeout(ContractForm.init, 0)
            });

            $scope.cancel = function () {
                $modalInstance.dismiss();
            };

            User.query(function(users){
                $scope.users = users;
            });

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
                        $modalInstance.dismiss();
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

            $modalInstance.opened.then(function() {
                setTimeout(ContractForm.init, 0)
            });

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
    ).factory('ContractForm', ['ValidationTool', function (ValidationTool) {
        return {
            init: function(){

                var config = {
                    rules: {
                        name: {
                            minlength: 6,
                            maxlength: 128,
                            required: true
                        },
                        customer: {
                            minlength: 2,
                            maxlength: 128,
                            required: true
                        },
                        user: 'required',
                        udc: 'required',
                        start_date: 'required',
                        end_date: 'required'
                    }
                };

                ValidationTool.init('#contractForm', config);
                ComponentsPickers.init();
              }
            }
        }]
    ).controller("ManageQuotaController", function(
        $rootScope, $scope, $modalInstance, $i18next,
        contract, resource_options, Quota, QuotaValidation,
        CommonHttpService, ToastrService, ResourceTool){

        $scope.contract = contract;

        $scope.resource_options = angular.copy(resource_options);

        $scope.resourceLabel = function(key){

            var label = '';

            for(var i=0; i < resource_options.length; i++){

                var option = resource_options[i];

                if(option[0] == key){
                    label = option[1];
                    break;
                }
            }

            return label;
        };

        $scope.quotas = Quota.query({contract_id: contract.id}, function(quotas){

            // filter options that has been created.
            $scope.resource_options = $scope.resource_options.filter(function(option){

                for(var i = 0; i < quotas.length; i++){
                    var quota = quotas[i];

                    if(quota.resource == option[0]) {
                        return false
                    }
                }

                return true;
            });
        });

        $modalInstance.opened.then(function() {
            setTimeout(function(){
                $scope.form = QuotaValidation.init();
            }, 0)
        });

        $scope.cancel = function () {
            $modalInstance.dismiss();
        };

        $scope.add_quota = function(resource_type){

            $scope.quotas.push({
                resource: resource_type,
                limit: 0,
                contract: contract.id
            });

            $scope.resource_options = $scope.resource_options.filter(function(option){
                return option[0] != resource_type;
            });

            $scope.form = QuotaValidation.init();

        };

        $scope.remove = function(toDel){

            var refresh = function(){

                $scope.quotas = $scope.quotas.filter(function(quota){
                    return quota.resource != toDel.resource;
                });
                $scope.resource_options.push([toDel.resource, $scope.resourceLabel(toDel.resource)]);
            };

            bootbox.confirm($i18next("contract.confirm_delete_quota"), function (confirmed) {

                if(!confirmed){
                    return;
                }
                if(toDel.id == undefined){
                    $scope.$apply(refresh);
                } else {
                    CommonHttpService.post("/api/quotas/delete/", {id: toDel.id}).then(function(data){
                        if (data.success) {
                            ToastrService.success(data.msg, $i18next("success"));
                            refresh();
                        } else {
                            ToastrService.error(data.msg, $i18next("op_failed"));
                        }
                    });
                }
            });
        };

        $scope.save = function(quota){

            if(!$scope.form.validate().valid()){
                return;
            }

            var params = ResourceTool.copy_only_data(quota);

            CommonHttpService.post("/api/quotas/create/", params).then(function(data){
                if (data.success) {
                    ToastrService.success(data.msg, $i18next("success"));
                    angular.copy(data.quota, quota);
                } else {
                    ToastrService.error(data.msg, $i18next("op_failed"));
                }
            });
        };

        $scope.submit = function(){

            if(!$scope.form.validate().valid()){
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
                } else {
                    ToastrService.error(data.msg, $i18next("op_failed"));
                }
            });
        };


    }).factory('QuotaValidation', ['ValidationTool', function(ValidationTool){
        return {
            init: function(){

            var config = {
                rules: {
                    'limit[]': {
                        required: true,
                        digits: true,
                        min: 1
                    }
                }
            };

            return ValidationTool.init('#quotaForm', config);
          }
        }
    }]);
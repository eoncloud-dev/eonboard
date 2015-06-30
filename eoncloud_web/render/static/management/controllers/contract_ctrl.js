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
    );
/**
 * User: bluven
 * Date: 15-6-25
 */


'use strict';

CloudApp.controller('ContractController',
    function ($rootScope, $scope, $filter, $timeout, $modal, ngTableParams, Contract) {
        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;

        $scope.contract_table = new ngTableParams({
            page: 1,
            count: 10
        },{
            counts: [],
            getData: function ($defer, params) {
                Contract.query(function (data) {

                    var data_list = $filter('orderBy')(data, params.orderBy());

                    params.total(data_list.length);

                    $scope.contacts = data_list.slice((params.page() - 1) * params.count(), params.page() * params.count());

                    $defer.resolve($scope.contacts);
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
                    },
                    contract: function(){return {}}
                }
            });
        };

        $scope.edit = function(contract){

            $modal.open({
                templateUrl: 'create.html',
                controller: 'ContractCreateController',
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
    })
    .controller('ContractCreateController',
        function($rootScope, $scope, $modalInstance, $i18next, contract, contract_table,
                 User, Contract, UserDataCenter, CommonHttpService, ToastrService){

            contract = angular.copy(contract);

            $scope.users = [];
            $scope.udcList = [];

            $scope.has_error=false;

            $scope.contract = contract;

            $modalInstance.opened.then(function() {
                setTimeout(function(){
                    ComponentsPickers.init();
                    FormWizard.init();
                }, 0)
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

                contract = angular.copy(contract);

                contract.start_date += " 00:00:00";
                contract.end_date += " 23:59:00";

                var url = null;
                if(contract.id){
                   url = "/api/contracts/create";
                } else {
                   url = "/api/contracts/update";
                }

                CommonHttpService.post(url, contract).then(function(data){
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
);
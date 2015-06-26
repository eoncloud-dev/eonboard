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

        $scope.create = function () {
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
    })
    .controller('ContractCreateController',
        function($rootScope, $scope, $modalInstance, $i18next, contract_table,
                 User, Contract, UserDataCenter, CommonHttpService, ToastrService){

            var contract = {};

            $scope.users = [];
            $scope.udcList = [];

            $scope.has_error=false;

            $scope.contract = contract;

            $modalInstance.opened.then(function(){
                ComponentsPickers.init();
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

            $scope.create = function(contract){

                CommonHttpService.post("/api/contracts/", contract).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        contract_table.reload();
                        $modalInstance.dismiss();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }

                });
            }
        }
);
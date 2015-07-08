/**
 * User: bluven
 * Date: 15-6-29
 * Time: 下午2:11
 **/

CloudApp.controller('FlavorController',
    function($rootScope, $scope, $filter, $modal, $i18next,
             CommonHttpService, ToastrService, ngTableParams,
             Flavor, CheckboxGroup){

        $scope.$on('$viewContentLoaded', function(){
                Metronic.initAjax();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;

        $scope.flavors = [];
        var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.flavors);

        $scope.flavor_table = new ngTableParams({
                page: 1,
                count: 10
            },{
                counts: [],
                getData: function ($defer, params) {
                    Flavor.query(function (data) {

                        var results = $filter('orderBy')(data, params.orderBy());
                        params.total(results.length);
                        $scope.flavors = results.slice((params.page() - 1) * params.count(), params.page() * params.count());
                        checkboxGroup.syncObjects($scope.flavors);
                        $defer.resolve($scope.flavors);
                    });
                }
            });

        $scope.edit = $scope.create = function(flavor) {

                flavor = flavor || {};

                $modal.open({
                    templateUrl: 'create.html',
                    controller: 'FlavorCreateController',
                    backdrop: "static",
                    size: 'lg',
                    resolve: {
                        flavor_table: function () {
                            return $scope.flavor_table;
                        },
                        flavor: function(){return flavor;}
                    }
                });
            };

        var deleteFlavors = function(ids){

            bootbox.confirm($i18next("flavor.confirm_delete"), function(confirmed){

                if(!confirmed){
                    return;
                }

                if(typeof ids == 'function'){
                    ids = ids();
                }

                CommonHttpService.post("/api/flavors/batch-delete/", {ids: ids}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.flavor_table.reload();
                        checkboxGroup.uncheck()
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

        $scope.batchDelete = function(){

            deleteFlavors(function(){
                var ids = [];

                checkboxGroup.forEachChecked(function(flavor){
                    if(flavor.checked){
                        ids.push(flavor.id);
                    }
                });

                return ids;
            });
        };

        $scope.delete = function(flavor){
            deleteFlavors([flavor.id]);
        };
    })

    .controller('FlavorCreateController',
        function($rootScope, $scope, $modalInstance,
                 flavor_table, flavor, Flavor, FlavorForm,
                 $i18next, CommonHttpService, ResourceTool, ToastrService){

            $scope.flavor = ResourceTool.copy_only_data(flavor);

            $modalInstance.rendered.then(FlavorForm.init);

            $scope.cancel = function () {
                $modalInstance.dismiss();
            };

            $scope.submit = function(flavor){

                if(!$("#flavorForm").validate().form()){
                    return;
                }

                var url = '/api/flavors';

                if(flavor.id){
                    url += "/update/";
                } else {
                    url += "/create/";
                }

                CommonHttpService.post(url, flavor).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        flavor_table.reload();
                        $modalInstance.dismiss();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            };
        }
    ).factory('FlavorForm', ['ValidationTool', function (ValidationTool) {
        return {
            init: function(){

                var config = {
                    rules: {
                        name: {
                            minlength: 2,
                            maxlength: 128,
                            required: true
                        },
                        cpu: {
                            required: true,
                            digits: true
                        },
                        memory: {
                            required: true,
                            digits: true
                        },
                        price: {
                            required: true,
                            number: true
                        }
                    }
                };

                ValidationTool.init('#flavorForm', config);
              }
            }
        }]);

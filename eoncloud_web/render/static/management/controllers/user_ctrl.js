/**
 * User: bluven
 * Date: 15-6-29
 * Time: 下午2:11
 **/

CloudApp.controller('UserController',
    function($rootScope, $scope, $filter, $modal, $i18next,
             CommonHttpService, ToastrService, ngTableParams, User){

        $scope.$on('$viewContentLoaded', function(){
                Metronic.initAjax();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;

        $scope.users = [];

        $scope.user_table = new ngTableParams({
                page: 1,
                count: 10
            },{
                counts: [],
                getData: function ($defer, params) {
                    User.query(function (data) {

                        var results = $filter('orderBy')(data, params.orderBy());

                        params.total(results.length);

                        $scope.users = results.slice((params.page() - 1) * params.count(), params.page() * params.count());

                        $defer.resolve($scope.users);
                    });
                }
            });

        $scope.deactivate = function(user){

            bootbox.confirm($i18next('user.confirm_deactivate'), function(confirmed){

                if(!confirmed){
                    return;
                }

                CommonHttpService.post("/api/users/deactivate/", {id: user.id}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.user_table.reload();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });

            });
        };

        $scope.activate = function(user){
            bootbox.confirm($i18next('user.confirm_activate'), function(confirmed){

                if(!confirmed){
                    return;
                }

                CommonHttpService.post("/api/users/activate/", {id: user.id}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.user_table.reload();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });

            });
        };
    });

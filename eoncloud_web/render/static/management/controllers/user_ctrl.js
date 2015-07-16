/**
 * User: bluven
 * Date: 15-6-29
 * Time: 下午2:11
 **/

CloudApp.controller('UserController',
    function($rootScope, $scope, $filter, $modal, $i18next,
             CommonHttpService, ToastrService, ngTableParams,
             User, ngTableHelper){

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
                        $scope.users = ngTableHelper.paginate(data, $defer, params);
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

        $scope.viewUdcList = function(user){
            $modal.open({
                templateUrl: 'udc_list.html',
                controller: 'UserUdcListController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    user: function(){
                        return User.get({id: user.id});
                    }
                }
            });
        };

        $scope.openPasswordModal = function(user){
            $modal.open({
                templateUrl: 'change-password.html',
                controller: 'ChangePasswordController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    user: function(){
                        return user;
                    }
                }
            });
        };
    })

    .controller('UserUdcListController',
        function($scope, $modalInstance, ngTableParams, user){

            $scope.cancel = $modalInstance.dismiss;

            $scope.udc_table = new ngTableParams({
                    page: 1,
                    count: 10
                },{
                    counts: [],
                    getData: function ($defer, params) {
                        user.$promise.then(function(){
                            $defer.resolve(user.user_data_centers);
                        });
                }
            });
    })

    .controller('ChangePasswordController',
        function($scope, $modalInstance, $i18next, ngTableParams,
                 CommonHttpService, ValidationTool, ToastrService,
                 user){

            var form = null;
            $scope.user = user = {id: user.id, old_password: '', new_password: '', confirm_password: ''};

            $scope.cancel = $modalInstance.dismiss;

            $modalInstance.rendered.then(function(){
                form = ValidationTool.init('#passwordForm');
            });

            $scope.changePassword = function(){

                if(!form.valid()){
                    return;
                }

                CommonHttpService.post('/api/users/change-password/', user).then(function(result){
                    if(result.success){
                        ToastrService.success(result.msg, $i18next("success"));
                        $modalInstance.dismiss();
                    } else {
                        ToastrService.error(result.msg, $i18next("op_failed"));
                    }
                });
            }
    });

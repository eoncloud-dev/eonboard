/**
 * User: bluven
 * Date: 15-6-29
 * Time: 下午2:11
 **/

CloudApp.controller('UserController',
    function($rootScope, $scope, $filter, $modal, $i18next, $ngBootbox,
             CommonHttpService, ToastrService, ngTableParams,
             CheckboxGroup, ngTableHelper, User){

        $scope.$on('$viewContentLoaded', function(){
                Metronic.initAjax();
        });

        $rootScope.settings.layout.pageBodySolid = true;
        $rootScope.settings.layout.pageSidebarClosed = false;

        $scope.users = [];
        var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.users);

        $scope.user_table = new ngTableParams({
                page: 1,
                count: 10
            },{
                counts: [],
                getData: function ($defer, params) {
                    User.query(function (data) {
                        $scope.users = ngTableHelper.paginate(data, $defer, params);
                        checkboxGroup.syncObjects($scope.users);
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

        var openBroadcastModal = function(users){
            $modal.open({
                templateUrl: 'broadcast.html',
                controller: 'BroadcastController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    users: function(){
                        return users;
                    },
                    notificationOptions: function(){
                        return CommonHttpService.get('/api/notifications/options/');
                    }
                }
            }).result.then(function(){
                   checkboxGroup.uncheck();
            });
        };

        $scope.openBroadcastModal = function(){
            openBroadcastModal(checkboxGroup.checkedObjects());
        };

        $scope.openNotifyModal = function(user){
            openBroadcastModal([user]);
        };

        $scope.openDataCenterBroadcastModal = function(){
            $modal.open({
                templateUrl: 'data_center_broadcast.html',
                controller: 'DataCenterBroadcastController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    notificationOptions: function(){
                        return CommonHttpService.get('/api/notifications/options/');
                    }
                }
            });
        };

        $scope.openAnnounceModal = function(){
            $modal.open({
                templateUrl: 'announce.html',
                controller: 'AnnounceController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    notificationOptions: function(){
                        return CommonHttpService.get('/api/notifications/options/');
                    }
                }
            });
        };

        $scope.initialize = function(user){

            $ngBootbox.confirm($i18next("user.confirm_initialize")).then(function(){
                CommonHttpService.post("/api/users/initialize/", {user_id: user.id}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.user_table.reload();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
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

    .controller('BroadcastController',
        function($scope, $modalInstance, $i18next, ngTableParams,
                 CommonHttpService, ValidationTool, ToastrService,
                 users, notificationOptions){

            var INFO = 1, form = null, options = [];

            angular.forEach(notificationOptions, function(option){
                options.push({key: option[0], label: [option[1]]});
            });

            $scope.users = users;
            $scope.options = options;
            $scope.cancel = $modalInstance.dismiss;
            $scope.notification = {title: '', content: '', level: INFO};

            $modalInstance.rendered.then(function(){
                form = ValidationTool.init('#notificationForm');
            });

            $scope.broadcast = function(notification){

                if(!form.valid()){
                    return;
                }

                var params = angular.copy(notification);

                if(users.length > 0){
                    params.receiver_ids = [];
                    angular.forEach(users, function(user){
                        params.receiver_ids.push(user.id);
                    });
                }

                CommonHttpService.post('/api/notifications/broadcast/', params).then(function(result){
                    if(result.success){
                        ToastrService.success(result.msg, $i18next("success"));
                        $modalInstance.close();
                    } else {
                        ToastrService.error(result.msg, $i18next("op_failed"));
                    }
                });
            }
    })

    .controller('AnnounceController',
        function($scope, $modalInstance, $i18next,
                 CommonHttpService, ValidationTool, ToastrService,
                 notificationOptions){

            var INFO = 1, form = null, options = [];

            angular.forEach(notificationOptions, function(option){
                options.push({key: option[0], label: [option[1]]});
            });

            $scope.options = options;
            $scope.cancel = $modalInstance.dismiss;
            $scope.notification = {title: '', content: '', level: INFO};

            $modalInstance.rendered.then(function(){
                form = ValidationTool.init('#notificationForm');
            });

            $scope.announce = function(notification){

                if(!form.valid()){
                    return;
                }

                var params = angular.copy(notification);

                CommonHttpService.post('/api/notifications/announce/', params).then(function(result){
                    if(result.success){
                        ToastrService.success(result.msg, $i18next("success"));
                        $modalInstance.close();
                    } else {
                        ToastrService.error(result.msg, $i18next("op_failed"));
                    }
                });
            }
    });

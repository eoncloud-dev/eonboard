/**
 * User: bluven
 * Date: 15-7-24 Time: 上午10:40
 */


CloudApp.controller('NotificationController',
    function($rootScope, $scope, Notification){

        $scope.$on('$viewContentLoaded', function() {
            Metronic.initAjax();
        });

        $scope.notifications = [];

        $scope.delete = function(notification){
            Notification.delete({id: notification.id}, function(){
                load();
            });
        };

        $scope.collapse = function(target){

            target.isCollapsed = !target.isCollapsed;

            angular.forEach($scope.notifications, function(notification){
                if(notification.id != target.id){
                    notification.isCollapsed = false;
                }
            });

        };

        var load = $scope.load = function(){
            Notification.query(function(notifications){
                $scope.notifications = notifications;
            });
        };

        load();
    })

    .controller('NotificationDetailController', function($scope, $modalInstance, notification){
        $scope.notification = notification;
        $scope.close = $modalInstance.close;
    });

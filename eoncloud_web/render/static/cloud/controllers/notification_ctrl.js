/**
 * User: bluven
 * Date: 15-7-17 Time: 下午3:11
 */


CloudApp.controller('NotificationController',
    function($rootScope, $scope, $modal, CommonHttpService, Notification){

    $scope.$on('$viewContentLoaded', function() {
        Metronic.initAjax();
    });

    var unreadList = [],
        readList = [],
        all = $scope.notifications = [];

    $scope.read = function(notification){
        $modal.open({
                templateUrl: 'detail.html',
                controller: 'NotificationDetailController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    notification: function () {
                        return notification;
                    }
                }
            }).result.then(function(){

                if(notification.is_read){
                   return;
                }

                Notification.markRead({id: notification.id}, function(){
                    notification.is_read = true;
                    split();
                });
            });
    };

    $scope.showAll = function(){
        $scope.notifications = all;
    };

    $scope.showReadList = function(){
        $scope.notifications = readList;
    };

    $scope.showUnreadList = function(){
        $scope.notifications = unreadList;
    };

    $scope.delete = function(notification){
        Notification.delete({id: notification.id}, function(){
            load();
        });
    };

    var split = function(){
        unreadList.splice(0, unreadList.length);
        readList.splice(0, readList.length);

        angular.forEach(all, function(notification){
            if(notification.is_read){
                readList.push(notification);
            } else {
               unreadList.push(notification);
            }
        });
    };

    var load = function(){
        Notification.query(function(notifications){
            all.splice(0, all.length);
            angular.forEach(notifications, function(notification){
                all.push(notification);
            });
            split();
        });
    };

    $rootScope.setInterval(load, 10000);

    load();
})

.controller('NotificationDetailController', function($scope, $modalInstance, notification){
    $scope.notification = notification;
    $scope.close = $modalInstance.close;
});

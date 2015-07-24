/**
 * User: bluven
 * Date: 15-7-17 Time: 下午3:11
 */


CloudApp.controller('NotificationController',
    function($rootScope, $scope, $modal, Feed){

    $scope.$on('$viewContentLoaded', function() {
        Metronic.initAjax();
    });

    $scope.feeds = [];

    $scope.unreadStyle = {'color': 'blue'};
    $scope.readStyle = {'color': 'gray'};

    $scope.delete = function(feed){
        Feed.delete({id: feed.id}, function(){
            load();
        });
    };

    $scope.collapse = function(target){

        target.isCollapsed = !target.isCollapsed;

        if(target.is_read == false){
            Feed.markRead({id: target.id}, function(){
                    target.is_read = true;
                });
        }

        angular.forEach($scope.feeds, function(feed){
            if(feed.id != target.id){
                feed.isCollapsed = false;
            }
        });

    };

    var load = $scope.load = function(){
        Feed.query(function(feeds){
            $scope.feeds = feeds;
        });
    };

    load();
})

.controller('NotificationDetailController', function($scope, $modalInstance, notification){
    $scope.notification = notification;
    $scope.close = $modalInstance.close;
});

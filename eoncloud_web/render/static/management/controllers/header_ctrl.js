/**
 * User: bluven
 * Date: 15-7-16 Time: 上午10:23
 */


CloudApp.controller('HeaderController',
    ['$rootScope', '$scope', '$http', function ($rootScope, $scope, $http) {
        $scope.$on('$includeContentLoaded', function () {
            Layout.initHeader(); // init header
        });

        $http({"method": "GET", "url": "/current_user/"}).success(function (data) {
            $rootScope.current_user = data;
        });
}]);

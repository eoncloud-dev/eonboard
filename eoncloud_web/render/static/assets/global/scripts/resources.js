/**
 * User: bluven
 * Date: 15-7-13 Time: 下午2:59
 */


angular.module('cloud.resources', [])

.factory('Image', ['$resource', function ($resource) {
    return $resource("/api/images/:id");
}])

.factory('Instance', ['$resource', function ($resource) {
    return $resource("/api/instances/:id");
}])

.factory('User', ['$resource', function($resource){
    return $resource("/api/users/:id", {id: '@id'})
}])

.factory('Contract', ['$resource', function($resource){
    return $resource("/api/contracts/:id");
}])

.factory('Quota', ['$resource', function($resource){
    return $resource("/api/quotas/:id", {id: '@id'}) ;
}])

.factory('Operation', ['$resource', function ($resource) {
    return $resource("/api/operation/:id", {}, {query: {isArray: false}});
}])

.factory('Flavor', ['$resource', function ($resource) {
    return $resource("/api/flavors/:id");
}])

.factory('Network', ['$resource', function ($resource) {
    return $resource("/api/networks/:id");
}])

.factory('Router', ['$resource', function ($resource) {
    return $resource("/api/routers/:id");
}])

.factory('Firewall', ['$resource', function ($resource) {
    return $resource("/api/firewall/:id");
}])

.factory('Volume', ['$resource', function ($resource) {
    return $resource("/api/volumes/:id");
}])

.factory('UserDataCenter', ['$resource', function($resource){
   return $resource("/api/user-data-centers/:id")
}])

.factory('DataCenter', ['$resource', function($resource){
  return $resource("/api/data-centers/:id")
}])

.factory('Forum', ['$resource', function($resource){
    return $resource("/api/forum/:id")
}])

.factory('ForumReply', ['$resource', function($resource){
    return $resource("/api/forum-replies/:id")
}])

.factory('Backup', ['$resource', function ($resource) {
    return $resource("/api/backup/:id");
}]);

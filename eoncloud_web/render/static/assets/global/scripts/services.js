/**
 * User: bluven
 * Date: 2015-7-13 2:36
 */

angular.module('cloud.services', [])

.factory('settings', ['$rootScope', function ($rootScope) {
    var settings = {
        layout: {
            pageSidebarClosed: false, // sidebar menu state
            pageBodySolid: false, // solid body color state
            pageAutoScrollOnLoad: 1000 // auto scroll to top on page load
        },
        layoutImgPath: Metronic.getAssetsPath() + 'admin/layout/img/',
        layoutCssPath: Metronic.getAssetsPath() + 'admin/layout/css/'
    };
    $rootScope.settings = settings;

    return settings;
}])

.factory("AuthInterceptor", [function($q){
    return {
        'responseError': function(rejection){
            if (rejection.status == 403 || rejection.status == 401) {
                window.location.href = "/login/";
                return $q.reject(rejection);
            }
            return rejection;
        }
    }
}])

.factory("CommonHttpService", function($http, $q){
    return {
        'get': function(api_url){
            var defer = $q.defer();
            $http({
                method: 'GET',
                url: api_url
            }).success(function(data, status, headers, config){
                defer.resolve(data);
            }).error(function(data, status, headers, config){
                defer.reject(data);
            });
            return defer.promise;
        },
        'post': function(api_url, post_data){
            var defer = $q.defer();
            $http({
                method: 'POST',
                url: api_url,
                data: $.param(post_data)
            }).success(function(data, status, headers,config){
                defer.resolve(data);
            }).error(function(data, status, headers, config){
                defer.reject(data);
            });
            return defer.promise;
        }
    };
})

.factory('ResourceTool', function(){
  return {
    'copy_only_data': function(data){

      var result = {};

      for(var attr in data){
        if(attr.startsWith('$') || attr == 'toJSON'){
          continue;
        }
        result[attr] = data[attr];
      }

      return result;
    }
  }
})

.factory('ToastrService', function () {
    toastr.options = {
        "closeButton": true,
        "debug": false,
        "positionClass": "toast-top-right",
        "onclick": null,
        "showDuration": "1000",
        "hideDuration": "1000",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    };
    return {
        success: function (message, title) {
            toastr.success(message, title);
        },
        warning: function (message, title) {
            toastr.warning(message, title);
        },
        error: function (message, title) {
            toastr.error(message, title);
        }
    };
})

.factory("BoxService", function(){
    return {
        "alert": function(message){
            bootbox.alert(message);
        },
        "confirm": function(message){
            bootbox.confirm(message, function(result) {
                return result;
            });
        }
    };
})

.factory('ValidationTool', function(){

    var defaultConfig = {
        onkeyup: false,
        doNotHideMessage: true,
        errorElement: 'span',
        errorClass: 'help-block help-block-error',
        focusInvalid: false,
        errorPlacement: function (error, element) {
            error.insertAfter(element);
        },

        highlight: function (element) {
            $(element).closest('.form-group').removeClass('has-success').addClass('has-error');
        },

        unhighlight: function (element) {
            $(element).closest('.form-group').removeClass('has-error').addClass('has-success');
        }
    };

    return {
        init: function(selector, config){

            config = config || {};

            for(var attr in defaultConfig){
                if(config[attr] === undefined){
                    config[attr] = defaultConfig[attr];
                }
            }
            $(selector).validate(config);

            return $(selector);
        }
    }
})

.factory('CheckboxGroup', function(){

    var init = function(objects, flagName){

        flagName = flagName || 'checked';

        var groupChecker = {
            objects: objects,
            checkedObjects: [],
            toggleAll: function(){
                var self = this;
                angular.forEach(self.objects, function(obj){
                    obj[flagName] = self[flagName];
                });
            },
            noneChecked: function(){
                var count = 0;

                angular.forEach(this.objects, function(obj){
                    if(obj[flagName]){
                        count += 1;
                    }
                });

                return count == 0;
            },
            syncObjects: function(objects){
                this.objects = objects;
            },
            uncheck: function(){
                this[flagName] = false;
                this.toggleAll();
            },
            forEachChecked: function(func){
                angular.forEach(this.objects, function(obj){
                    if(obj[flagName]){
                       func(obj);
                    }
                });
            }
        };

        groupChecker[flagName] = false;

        return groupChecker;
    };

    return {init: init};

})

/* Init date pickers */
.factory('DatePicker', function (){

    var initDatePickers = function(){
        if (jQuery().datepicker) {
            $('.date-picker').datepicker({
                rtl: Metronic.isRTL(),
                orientation: "left",
                format: 'yyyy-mm-dd',
                autoclose: true
            });
        }
    };

    return {
        initDatePickers: initDatePickers
    }
});

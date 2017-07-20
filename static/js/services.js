/**
 * Created by jiangweiwei on 16/11/29.
 */

var service = angular.module('WebService', ['ngResource']);

/**
 * 工厂类    将请求送到对应的api
 * DataForQuery  单条记录的增加  整个数据集合信息返回
 * DataForSingle 单条记录的删改查  注意id
 * DataForPagination 点击页面选择时刷新整个页面数据
*/

service.factory('DataForQuery', function ($resource) {
    return $resource('api/v1/getinfo')
});

service.service('popupService',function($window){
    this.showPopup=function(message){
        return $window.confirm(message);
    }
});

service.factory('DataForSingle', function ($resource) {
    return $resource('api/v1/getinfo/:id', {id: '@id'}, {
        update: {
            method: 'PUT' // this method issues a PUT request
        }
    })
});

service.factory('DataForPagination', function ($resource) {
    return $resource('api/v1/getdata',
        {},
        {
            save: {
                method: 'POST',
                isArray: false
            }
        });
});

service.factory('AddAppVersion', function ($resource) {
    return $resource('api/v1/add_version')
});

service.factory('CheckPass', function ($resource) {
    return $resource('api/v1/login')
});

service.factory('LogInfo', function ($resource) {
    return $resource('api/v1/log_server/:type',
        {},
        {
            save: {
                method: 'POST',
                isArray: false
            }
        })
});

service.factory('LogInfoInPage', function ($resource) {
    return $resource('api/v1/log_server/check_for_current_page',
        {},
        {
            save: {
                method: 'POST',
                isArray: false
            }
        })
});

service.factory('LoginfoByPage', function ($resource) {
    return $resource('api/v1/log_server/:pagenumber/:numPerPage',
        {},
        {
            save: {
                method: 'POST',
                isArray: false
            }
        })
});

service.factory('AuthService', function ($resource) {
    return $resource('api/v1/status')
});

service.factory('logout', function ($resource) {
    return $resource('api/v1/logout')
});
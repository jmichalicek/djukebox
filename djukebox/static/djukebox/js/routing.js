/*
* Routing of URLs to correct views/templates
* Author: Justin Michalicek
*/

// Router.routes should be a list of lists of
// [regularExpression, functionCallable, {additional data}]

var router = Object.create(Object.prototype);

Object.defineProperty(router, 'routes', {
    value: [],
    writable: true,
    enumerable: true,
    configurable: false
});

router.routeToView = function () {
    // Just route on hash fragment for now
    var hashpath = window.location.hash.replace('#', '');

    $.each(this.routes, function(index, value) {
        if(value[0].test(hashpath)) {
            value[1](value[2]);
	    return false;
        }
    });
};
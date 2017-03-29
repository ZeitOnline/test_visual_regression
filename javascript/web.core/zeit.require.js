/*globals requirejs */

define([ 'requirejs' ], function() {

    function clear( queue ) {
        for ( var i = 0, l = queue.length; i < l; i++ ) {
            requirejs.apply( window, queue[ i ]);
        }
    }

    return {
        clear: clear
    };
});

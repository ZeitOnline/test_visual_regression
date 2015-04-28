/**
 * @fileOverview jQuery Plugin for debouncing function calls
 * @version  0.1
 */

(function( $ ) {

    'use strict';

    $.extend({
        /**
         * Creates a function that delays the invocation of `func` until after `wait`
         * milliseconds have elapsed since the last time it was invoked. If `immediate`
         * is passed, trigger the function on the leading edge, instead of the trailing.
         * @memberOf jQuery
         * @category Function
         * @param {Function} func The function to debounce.
         * @param {number} wait The number of milliseconds to delay.
         * @param {boolean} [immediate] invoke `func` on the leading edge of the timeout
         */
        debounce: function( func, wait, immediate ) {
            var timeout;

            return function() {
                var context = this,
                    args = arguments;

                if ( timeout ) {
                    clearTimeout( timeout );
                } else if ( immediate ) {
                    func.apply( context, args );
                }

                timeout = setTimeout(function() {
                    timeout = null;
                    if ( !immediate ) {
                        func.apply( context, args );
                    }
                }, wait );
            };
        }
    });

})( jQuery );

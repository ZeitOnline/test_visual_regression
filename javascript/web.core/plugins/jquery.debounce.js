/**
 * @fileOverview jQuery Plugin for debouncing function calls
 * @version  0.1
 */

(function( $ ) {

    'use strict';

    $.extend({
        /**
         * Creates a function that delays the invocation of `fn` until after `timeout`
         * milliseconds have elapsed since the last time it was invoked. If `invokeAsap`
         * is passed, trigger the function on the leading edge, instead of the trailing.
         * @memberOf jQuery
         * @category Function
         * @param {Function} fn The function to debounce.
         * @param {number} timeout The number of milliseconds to delay.
         * @param {boolean} [invokeAsap] invoke `fn` on the leading edge of the timeout
         */
        debounce: function(fn, timeout, invokeAsap, context) {

            if (arguments.length === 3 && typeof invokeAsap !== 'boolean') {
                context = invokeAsap;
                invokeAsap = false;
            }

            var timer;

            return function() {

                var args = arguments;
                context = context || this;

                if (invokeAsap && !timer) {
                    fn.apply(context, args);
                }

                clearTimeout(timer);

                timer = setTimeout(function() {
                    if (!invokeAsap) {
                        fn.apply(context, args);
                    }

                    timer = null;
                }, timeout);
            };
        }
    });

})( jQuery );

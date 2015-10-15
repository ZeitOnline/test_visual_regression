/**
 * @fileOverview jQuery Plugin for throttling event based function calls
 * @version  0.1
 */

(function( $ ) {

    'use strict';

    $.extend({
        /**
         * Returns a function, that, when invoked, will only be triggered at most once
         * during a given window of time. Normally, the throttled function will run
         * as much as it can, without ever going more than once per `wait` duration;
         * but if you'd like to disable the execution on the leading edge, pass
         * `{leading: false}`. To disable execution on the trailing edge, ditto.
         * @memberOf jQuery
         * @category Function
         * @param {Function} func The function to throttle.
         * @param {number} wait The number of milliseconds to delay.
         * @param {object} [options] disable the invocation on the leading edge `{leading: false}` or end of timeout `{trailing: false}`
         */
        throttle: function( func, wait, options ) {
            options = options || {};
            var context, args, result,
                timeout = null,
                previous = 0,
                getNow = Date.now || function() {
                    return new Date().getTime();
                },
                later = function() {
                    previous = options.leading === false ? 0 : getNow();
                    timeout = null;
                    result = func.apply( context, args );
                    if ( !timeout ) {
                        context = args = null;
                    }
                };
            return function() {
                var now = getNow();
                if ( !previous && options.leading === false ) {
                    previous = now;
                }
                var remaining = wait - ( now - previous );
                context = this;
                args = arguments;
                if ( remaining <= 0 || remaining > wait ) {
                    if ( timeout ) {
                        clearTimeout( timeout );
                        timeout = null;
                    }
                    previous = now;
                    result = func.apply( context, args );
                    if ( !timeout ) {
                        context = args = null;
                    }
                } else if ( !timeout && options.trailing !== false ) {
                    timeout = setTimeout( later, remaining );
                }
                return result;
            };
        }
    });
})( jQuery );

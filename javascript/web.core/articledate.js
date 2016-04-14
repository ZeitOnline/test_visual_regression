/**
 * @fileOverview Module for swaping text, used to obfuscate article date for google
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
define([ 'jquery' ], function( $ ) {
    return {
        init: function() {
            var dates = $( '.encoded-date' );

            if ( dates.length ) {
                /**
                 * require jquery.clarify
                 */
                require([
                    'jquery.clarify'
                ], function() {
                    dates.clarify();
                });
            }
        }
    };
});

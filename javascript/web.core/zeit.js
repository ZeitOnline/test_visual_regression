/**
 * @fileOverview ZEIT ONLINE core javascript module [Zeit]
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */

// ES6 Promise polyfill
// @see https://webpack.js.org/guides/code-splitting-import/#promise-polyfill
require( 'es6-promise/auto' );

var Zeit = window.Zeit || {},
    extension = {
        clearQueue: function() {
            // ensure this extended window.Zeit
            if ( typeof this.queue !== 'object' ) {
                return;
            }

            if ( this.queue.length ) {
                var queue = this.queue;

                require([ 'web.core/zeit.require' ], function( amd ) {
                    amd( queue );
                });

                this.queue = [];
            }
        }
    },
    key;

for ( key in extension ) {
    if ( extension.hasOwnProperty( key ) ) {
        Zeit[ key ] = extension[ key ];
    }
}

Zeit.debounce = require( 'web.core/debounce' );
Zeit.throttle = require( 'web.core/throttle' );
// special app functionality
if ( Zeit.isWrapped || window.location.href.indexOf( 'force-userisback' ) !== -1 ) {
    Zeit.appUserIsBack = require( 'web.core/appUserIsBack' );
}

if ( Zeit.isWrapped || window.location.href.indexOf( 'force-userfeedback' ) !== -1 ) {
    Zeit.appUserFeedback = require( 'web.core/appUserFeedback' );
}

module.exports = Zeit;

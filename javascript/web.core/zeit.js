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
        },
        cookieCreate: function( name, value, days, domain ) {
            var expires = '';

            if ( arguments.length < 4 ) {
                domain = 'zeit.de';
            }

            if ( days ) {
                var date = new Date();
                date.setTime( date.getTime() + ( days * 24 * 60 * 60 * 1000 ) );
                expires = '; expires=' + date.toGMTString();
            }

            document.cookie = name + '=' + value + expires + '; path=/; domain=' + domain;
        },
        cookieRead: function( name ) {
            return ( document.cookie.match( '(?:^|;) ?' + name + '\\s*=\\s*([^;]*)' ) || 0 )[ 1 ];
        },
        isWrapped: navigator.userAgent.indexOf( 'ZONApp' ) > -1
    },
    key;

for ( key in extension ) {
    if ( extension.hasOwnProperty( key ) ) {
        Zeit[ key ] = extension[ key ];
    }
}

Zeit.debounce = require( 'web.core/debounce' );
Zeit.throttle = require( 'web.core/throttle' );
// speciak app functionality
//if ( Zeit.isWrapped ) {
Zeit.appUserIsBack = require( 'web.core/appUserIsBack' );
//}

module.exports = Zeit;

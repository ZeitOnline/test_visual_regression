/**
 * @fileOverview jQuery Plugin to clarify obfuscated text
 * @author moritz.stoltenburg@zeit.de
 * @version 0.1
 */
(function( factory ) {
    if ( typeof define === 'function' && define.amd ) {
        // AMD
        define( [ 'jquery' ], factory );
    } else if ( typeof exports === 'object' ) {
        // Node, CommonJS
        module.exports = factory( require( 'jquery' ) );
    } else {
        // Browser globals
        factory( jQuery );
    }
}(function( $ ) {
    /**
     * @see https://github.com/yckart/jquery.base64.js
     * Based upon: https://gist.github.com/Yaffle/1284012
     * Copyright (c) 2012 Yannick Albert (http://yckart.com)
     * Licensed under the MIT license (http://www.opensource.org/licenses/mit-license.php).
     **/
    var b64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/',
        a256 = '',
        r64 = [ 256 ],
        r256 = [ 256 ],
        i = 0;

    while ( i < 256 ) {
        var c = String.fromCharCode( i );
        a256 += c;
        r256[i] = i;
        r64[i] = b64.indexOf( c );
        ++i;
    }

    function code( s, discard, alpha, beta, w1, w2 ) {
        s = String( s );
        var buffer = 0,
            i = 0,
            length = s.length,
            result = '',
            bitsInBuffer = 0;

        while ( i < length ) {
            var c = s.charCodeAt( i );
            c = c < 256 ? alpha[c] : -1;

            buffer = ( buffer << w1 ) + c;
            bitsInBuffer += w1;

            while ( bitsInBuffer >= w2 ) {
                bitsInBuffer -= w2;
                var tmp = buffer >> bitsInBuffer;
                result += beta.charAt( tmp );
                buffer ^= tmp << bitsInBuffer;
            }
            ++i;
        }

        if ( !discard && bitsInBuffer > 0 ) {
            result += beta.charAt( buffer << ( w2 - bitsInBuffer ) );
        }

        return result;
    }

    var base64 = {
        encode: function( plain ) {
            plain = code( plain, false, r256, b64, 8, 6 );
            return plain + '===='.slice(( plain.length % 4 ) || 4 );
        },

        decode: function( coded ) {
            coded = coded.replace( /[^A-Za-z0-9\+\/\=]/g, '' );
            coded = String( coded ).split( '=' );
            var i = coded.length;
            do {--i;
                coded[i] = code( coded[i], true, r64, a256, 6, 8 );
            } while ( i > 0 );
            return coded.join( '' );
        }
    };

    if ( !window.btoa ) { window.btoa = base64.encode; }
    if ( !window.atob ) { window.atob = base64.decode; }

    $.fn.clarify = function() {
        return this.each( function() {
            $( this ).html( atob( this.getAttribute( 'data-obfuscated' ) ) );
        });
    };

}));

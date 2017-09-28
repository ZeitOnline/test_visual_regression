/**
 * @fileOverview function for showing an update alert in the app
 * @version  0.1
 * @author  nico.bruenjes@zeit.de
 */

function appUserIsBack( timestamp, options ) {
    'use strict';

    options = options || {};

    function AppUserIsBack( timestamp, options ) {
        this.defaults = {
            buttontext: 'Neu laden',
            delta: 5 * 60 * 1000, // 5 minutes
            debug: window.location.href.indexOf( 'debug-userisback' ) !== -1,
            endpoint: window.location.protocol + '//' + window.location.host + '/json/update-time',
            text: 'Die Seite wurde aktualisiert',
            force: window.location.href.indexOf( 'force-userisback' ) !== -1,
            slug: window.location.pathname
        };
        this.options = this.mixit( options, this.defaults );
        this.init();
    }

    AppUserIsBack.prototype.mixit = function( obj ) {
        var has = function( obj, prop ) {
                return hasOwnProperty.call( obj, prop );
            },
            args = Array.prototype.slice.call( arguments, 1 ),
            i = 0, len = args.length;

        for ( ;i < len; i += 1 ) {
            var mixin = args[ i ];
            // loop all properties in mixin
            for ( var prop in mixin ) {
                if ( has( mixin, prop ) ) {
                    if ( !has( obj, prop ) ) {
                        obj[ prop ] = mixin[ prop ];
                    } else {
                        if ( typeof mixin[ prop ] === 'object' && typeof obj[ prop ] === 'object' ) {
                            // recursion!
                            obj[ prop ] = this.mixit( obj[ prop ], mixin[ prop ]);
                        }
                    }
                }
            }
        }
        return obj;
    };

    AppUserIsBack.prototype.get = function( url ) {
        // Promises working since iOS Safari8, Android Browser 4.4.4
        return new window.Promise( function( resolve, reject ) {
            var xhr = new XMLHttpRequest();
            xhr.open( 'GET', url );
            xhr.onload = function() {
                // This is called even on 404 etc
                // so check the status
                if ( xhr.status === 200 ) {
                    // Resolve the promise with the response text
                    resolve( JSON.parse( xhr.response ) );
                } else {
                    // Otherwise reject with the status text
                    // which will hopefully be a meaningful error
                    reject( Error( xhr.statusText ) );
                }
            };
            // Handle network errors
            xhr.onerror = function() {
                reject( Error( 'Network Error' ) );
            };
            // Make the request
            xhr.send();
        });
    };

    AppUserIsBack.prototype.log = function() {
        if ( this.options.debug || this.options.force ) {
            var args = [];
            if ( arguments.length === 0 ) {
                return;
            } else if ( arguments.length === 1 ) {
                console.log.apply( console, arguments );
            } else {
                Array.prototype.push.apply( args, arguments );
                console[ args.shift() ].apply( console, args );
            }
        }
    };

    AppUserIsBack.prototype.getJSON = function( url, successHandler, errorHandler ) {
        var xhr = typeof XMLHttpRequest !== 'undefined' ? new XMLHttpRequest() : new window.ActiveXObject( 'Microsoft.XMLHTTP' );
        xhr.open( 'get', url, true );
        xhr.onreadystatechange = function() {
            var status;
            var data;
            // https://xhr.spec.whatwg.org/#dom-xmlhttprequest-readystate
            if ( xhr.readyState === 4 ) { // `DONE`
                status = xhr.status;
                if ( status === 200 ) {
                    data = JSON.parse( xhr.responseText );
                    if ( successHandler ) {
                        successHandler( data );
                    }
                } else {
                    if ( errorHandler ) {
                        errorHandler( status );
                    }
                }
            }
        };
        xhr.send();
    };

    AppUserIsBack.prototype.showUpdateWindow = function() {
        this.log( 'show update window' );
        var button = '<div class="user-is-back__button">' + this.options.buttontext + '</div>',
            text = '<div class="user-is-back__text">' + this.options.text + '</div>',
            container = document.createElement( 'div' );
        container.className = 'user-is-back';
        container.innerHTML = text + button;
        document.body.appendChild( container );
    };

    AppUserIsBack.prototype.init = function() {
        if ( !window.Promise ) {
            return;
        }
        var that = this,
            now = Date.now();
        this.get( options.endpoint + options.slug ).then( function( response ) {
            if (
                that.options.force ||
                ( response.last_published_semantic &&
                ( now - Date.parse( response.last_published_semantic ) ) >= that.options.delta )
            ) {
                that.log( 'info', 'lps: ' + response.last_published_semantic, 'now: ' + now  );
                that.showUpdateWindow();
            }
        }, function( error ) {
            that.log( 'error', error );
        });
    };

    new AppUserIsBack( timestamp, options );

}

module.exports = appUserIsBack;

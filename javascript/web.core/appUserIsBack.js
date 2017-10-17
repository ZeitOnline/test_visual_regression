/**
 * @fileOverview function for showing an update alert in the app
 * @version  0.1
 * @author  nico.bruenjes@zeit.de
 */

/**
 * check if a page is old in cache and show an unobstruvie info with reload button
 * @param  {int} timestamp unix timestamp of the last cache, fallbacks to 'now'
 * @param  {object} options   override defaults by passing an object with new values
 * @return void
 */
function appUserIsBack( timestamp, options ) {
    'use strict';

    options = options || {};

    function AppUserIsBack( timestamp, options ) {

        /**
         * default options
         * @type {Object}
         * @property {string} buttontext    text for the reload button 'Neu laden'
         * @property {boolean} debug        activate debugging (normally url(?|#)debug-userisback)
         * @property {int} delta            minimum time delta between cache and page semantic update time
         * @property {string} endpoint      api endpoint for checking update time
         * @property {boolean} force        activate debugging and forcing info message to show
         *                                  even on new page (normally url(?|#)force-userisback)
         * @property {string} link          link where the reload link is directed (in nojs mode)
         * @property {string} slug          pathname of the file to test for update time
         * @property {string} text          text of the info 'Die Seite wurde aktualisiert'
         */
        var defaults = {
            buttontext: 'Neu laden',
            debug: window.location.href.indexOf( 'debug-userisback' ) !== -1,
            delta: 0, // give higher deltas to show lesser messages
            endpoint: window.location.protocol + '//' + window.location.host + '/json/update-time',
            force: window.location.href.indexOf( 'force-userisback' ) !== -1,
            link: window.location.href,
            slug: window.location.pathname,
            text: 'Die Seite wurde aktualisiert'
        };

        this.options = this.mixit( options, defaults );
        this.timestamp = timestamp || Date.now();
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

    /**
     * plain vanilla get json with promise return
     * @param  {string} url        endpoint url
     * @return {promise}
     */
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

    /**
     * logging function - log to console only if debug or force mode aktivated
     * @return void
     */
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

    /**
     * tracking function - send events (load, click) to webtrekk
     * @return void
     */
    AppUserIsBack.prototype.track = function( action ) {
        this.log( 'Track: ' + action );
        var that = this;
        require([ 'web.core/clicktracking' ], function( Clicktracking ) {
            var data = [ 'appuserisback....' + action, that.options.link.replace( 'http://', '' ) ];
            Clicktracking.send( data );
        });


    };

    /**
     * show the update message at window bottom
     * @return void
     */
    AppUserIsBack.prototype.showUpdateMessage = function() {
        this.log( 'show update window' );
        if ( this.options.force ) {
            this.log( 'Forced display of message' );
        }
        var template = require( 'web.core/templates/appUserIsBack.html' ),
            html = template({
                text: this.options.text,
                buttontext: this.options.buttontext,
                link: this.options.link,
                linkForTracking: this.options.link.replace( 'http://', '' )
            });
        document.querySelector( 'body' ).insertAdjacentHTML( 'beforeend', html );
        this.track( 'appear' );

        var that = this; // to use inside the callbacks for that.track()

        document.querySelector( '#app-user-is-back' ).addEventListener( 'click', function() {
            that.track( 'refreshButton' );
        });
        document.querySelector( '#app-user-is-back' ).addEventListener( 'touch', function() {
            that.track( 'refreshButton' );
        });

        // enable user to to swipe the message off from the screen
        require([
            'jquery',
            'web.core/plugins/jquery.onSwipe'
        ], function( $ ) {
            $( '#app-user-is-back' ).onSwipe(
                function( element, swipeDirection ) {
                    if ( swipeDirection === 'left' || swipeDirection === 'right' ) {
                        // uppercase the first letter, to use it as velocity transition name
                        swipeDirection = swipeDirection.charAt( 0 ).toUpperCase() + swipeDirection.slice( 1 );
                        $( element ).velocity( 'transition.slide' + swipeDirection + 'Out', {
                            duration: 500,
                            complete: function() {
                                element.parentNode.removeChild( element );
                            }
                        });
                        that.track( 'remove' );
                    }
                }
            );
        });

    };

    AppUserIsBack.prototype.init = function() {
        if ( !window.Promise || document.querySelector( '#app-user-is-back' ) ) {
            return;
        }
        var that = this;
        this.get( options.endpoint + options.slug ).then( function( response ) {
            // check if the website was updated after the page was cached by the app
            if (
                that.options.force ||
                ( response.last_published_semantic &&
                ( Date.parse( response.last_published_semantic ) - that.timestamp ) >= that.options.delta )
            ) {
                that.log( 'info', 'lps: ' + Date.parse( response.last_published_semantic ),
                    'now: ' + that.timestamp, 'diff: ',
                    that.timestamp - Date.parse( response.last_published_semantic ) );
                that.showUpdateMessage();
            }
        }, function( error ) {
            that.log( 'error', error );
        });
    };

    new AppUserIsBack( timestamp, options );

}

module.exports = appUserIsBack;

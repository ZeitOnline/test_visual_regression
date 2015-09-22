/*
* Zeit Online HP Overlay
*
* Copyright (c) 2014 ZEIT ONLINE, http://www.zeit.de
* Dual licensed under the MIT and GPL licenses:
* http://www.opensource.org/licenses/mit-license.php
* http://www.gnu.org/licenses/gpl.html
*
* @author Anika Szuppa
* @author Nico Brünjes
*
* @requires ZEIT-Lib
*/

(function( $, ZMO, console, overlayConf ) {
    $.fn.hpOverlay = function( options ) {
        // defaults are overwritten by
        // http://scripts.zeit.de/static/js/hpoverlay.config.js
        var defaults = $.extend( {
            cookieTimeInDays: 1.5,
            countingPrefix: 'refreshbox',
            endpoint: 'http://www.zeit.de/json_update_time/index?callback=?',
            homepage: 'http://www.zeit.de/index',
            minutes: 5,
            isOn: true,
            timestamp: '',
            updateTime: 1,
            debug: ( ZMO.getQueryVar( 'aktPopDebug' ) && console && console.info && console.warn ) || false
        }, options ),
        //global timer
            timer = false,
        //define overlay functions
            overlay = {
            prependHtml: function() {
                // prepend html to body
                if ( $( '.overlay' ).size() < 1 ) {
                    $( 'body' ).prepend( $( '#overlay' ).html() );
                }
                $( '.overlay' ).fadeIn();
                $( '.lightbox' ).show();
            },
            clickCancel: function() {
                // action when cancel was clicked
                $( '.lightbox' ).hide();
                $( '.overlay' ).hide();
                ZMO.cookieCreate( 'overlaycanceled', 1, defaults.cookieTimeInDays, '' );
                window.clearTimeout( timer );
                $( document ).off( 'keypress scroll click mousemove' );
                if ( defaults.debug ) {
                    console.info( 'AktPop cancelled.' );
                }
            },
            clickReload: function() {
                // action when reload button or overlay was clicked
                location.reload();
            },
            bindClickEvents: function() {
                // bind click event for lightbox
                var that = this;

                // cancel button
                $( '.lightbox-cancel' ).on( 'click', function( event ) {
                    event.preventDefault();
                    that.clickCancel();
                });

                // reload
                $( '.overlay, .lightbox-button' ).on( 'click', function( event ) {
                    event.preventDefault();
                    that.clickReload();
                });

                // escape key
                $( window ).on( 'keyup', function( event ) {
                    if ( event.keyCode === 27 ) {
                        that.clickReload();
                    }
                });
            },
            restartTimer: function( time ) {
                time = time || defaults.minutes;
                // clear and restart timer
                if ( !$( '.overlay' ).is( ':visible' ) ) {
                    window.clearTimeout( timer );
                    overlay.addTimer( time );
                    if ( defaults.debug ) {
                        console.info( 'Timer restarted.' );
                    }
                }
            },
            bindResetEvents: function() {
                // bind events to reset timer
                var that = this;
                $( document ).on( 'keypress scroll click mousemove', function() {
                    that.restartTimer();
                });
            },
            addTimer: function( min ) {
                // add timer
                if ( defaults.debug ) {
                    console.info( 'mins: ', min );
                }
                var timeout = min * 60 * 1000;
                timer = window.setTimeout( initPopup, timeout );
            },
            updateTime: function() {
                var that = this,
                    request = $.ajax( defaults.endpoint, { dataType: 'jsonp' } );

                request.done( function( data ) {
                    // json anfrage ist fertig
                    defaults.timestamp = data.lastPublishedSemantic;
                    that.addTimer( defaults.minutes );
                } );
            },
            isLiveServer: function() {
                return !window.location.hostname.search( /(www.)?zeit\.de/ );
            }
        };

        //initialise popover
        function initPopup() {
            var request = $.ajax( defaults.endpoint, { dataType: 'jsonp' } );

            request.done( function( data ) {
                if ( defaults.debug ) {
                    console.info( defaults.timestamp, data.lastPublishedSemantic );
                }

                if ( defaults.timestamp !== data.lastPublishedSemantic ) {
                    if ( defaults.debug ) {
                        console.info( 'Page was updated.' );
                    }
                    overlay.prependHtml();
                    overlay.bindClickEvents();
                } else {
                    if ( defaults.debug ) {
                        console.info( 'JSON call found no page update.' );
                    }
                    overlay.restartTimer( defaults.updateTime );
                }
            });
        }

        return this.each( function() {
            if ( !overlay.isLiveServer() && !defaults.debug ) {
                console.warn( 'AktPopup cancelled because not on live server.' );
                return this;
            }

            // overwrite settings with external config file
            if ( overlayConf ) {
                defaults = $.extend( defaults, overlayConf );
            }

            var cookie = ZMO.cookieRead( 'overlaycanceled' );

            // only start timer if there's no mobile view, cookie wasn't set and it is switched on
            if ( !ZMO.isMobileView() && cookie !== 1 && defaults.isOn ) {
                if ( defaults.debug ) {
                    console.info( 'AktPop started w/ minutes: ', defaults.minutes, ' and updateTime: ', defaults.updateTime );
                }
                overlay.bindResetEvents();
                overlay.updateTime();
            } else {
                if ( defaults.debug ) {
                    console.warn( 'Cookie present or mobile view, action stopped.' );
                }
                return this;
            }

        });

    };//end of plugin
})( jQuery, window.ZMO, window.console, window.overlayConf );

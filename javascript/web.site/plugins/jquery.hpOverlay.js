// jscs:disable requireCamelCaseOrUpperCaseIdentifiers
/* global overlayConf */
/**
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

(function( $, window, document, ZMO ) {
    'use strict';

    // options may be overwritten by hpoverlay.config.js
    var options = {
            cookieTimeInDays: 1.5,
            endpoint: location.protocol + '//' + location.host + '/json_update_time/index',
            config: ZMO.scriptsURL + '/hpoverlay.config.js',
            minutes: 5,
            isOn: true,
            updateTime: 1,
            debug: location.search.indexOf( 'debug-popover' ) !== -1,
            force: location.search.indexOf( 'force-popover' ) !== -1
        },
        // define overlay object
        overlay = {
            activeElement: null,
            initialized: false,
            timer: false,
            timestamp: null,
            visible: false,
            show: function() {
                // show overlay
                var wrapper = $( '#overlay-wrapper' );

                if ( wrapper.not( ':visible' ) ) {
                    wrapper.show();
                    // fake "appear" event
                    wrapper.find( '.overlay-tracker' ).trigger( 'click' );
                }

                this.visible = true;
                // save focused element
                this.activeElement = document.activeElement;
                wrapper.find( '.overlay' ).fadeIn();
                wrapper.find( '.lightbox' ).show();
                wrapper.find( 'button' ).focus();
                this.bindEvents();

                $( document ).off( '.modal' );
            },
            cancel: function() {
                // action when cancel was clicked
                window.clearTimeout( this.timer );
                $( '.lightbox' ).hide();
                $( '.overlay' ).hide();
                $( '#overlay-wrapper' ).hide();
                this.visible = false;
                ZMO.cookieCreate( 'overlaycanceled', 1, options.cookieTimeInDays, '' );

                // restore last focused element
                if ( this.activeElement ) {
                    this.activeElement.focus();
                }

                this.log( 'Refresh page cancelled' );
            },
            reload: function() {
                // action when reload button or overlay was clicked
                location.reload();
            },
            bindEvents: function() {
                if ( this.initialized ) {
                    return;
                }

                // bind events for lightbox
                var that = this;

                // cancel button
                $( '.lightbox-cancel' ).on( 'click', function( event ) {
                    event.preventDefault();
                    that.cancel();
                });

                // reload
                $( '.overlay, .lightbox-button' ).on( 'click', function( event ) {
                    event.preventDefault();
                    that.reload();
                });

                // escape key
                $( window ).on( 'keyup', function( event ) {
                    if ( event.keyCode === 27 ) {
                        that.reload();
                    }
                });

                this.initialized = true;
            },
            bindResetEvents: function() {
                // bind events to reset timer, need to debounce at least scroll and mousemove event
                var that = this;
                $( document ).on( 'keypress.modal scroll.modal click.modal mousemove.modal', $.debounce( function() {
                    that.setTimeout();
                }, 1000 ));
            },
            setTimeout: function( time ) {
                var that = this,
                    minutes = time || options.minutes;

                if ( this.timer ) {
                    // clear timer
                    window.clearTimeout( this.timer );
                }

                // start new timer
                if ( !this.visible ) {
                    this.timer = window.setTimeout( function() { that.init(); }, minutes * 60 * 1000 );
                    this.log( 'New timer started for ' + minutes + ' minutes' );
                }
            },
            init: function() {
                var that = this;

                $.ajax( options.endpoint, { dataType: 'json' } )
                    .done( function( data ) {
                        that.log( 'timestamp:', that.timestamp, 'modified:', data.last_published_semantic );

                        if ( !that.timestamp ) {
                            that.log( 'No timestamp stored, initializing popover.' );
                            that.timestamp = data.last_published_semantic;
                            that.setTimeout();
                        } else if ( data.last_published_semantic && that.timestamp !== data.last_published_semantic ) {
                            that.log( 'Page was updated' );
                            that.show();
                        } else {
                            that.log( 'JSON call found no page update' );
                            that.setTimeout( options.updateTime );
                        }
                    })
                    .fail( function() {
                        that.setTimeout( options.updateTime );
                    });
            },
            isLiveServer: function() {
                return /^(www\.)?zeit\.de$/.test( location.hostname );
            },
            config: function() {
                var that = this;

                $.ajax( options.config, { dataType: 'script', cache: true } )
                    .done( function() {
                        $.extend( options, overlayConf );

                        // check if popup is switched on
                        if ( options.isOn  ) {
                            that.log( 'Initialize popup w/ minutes:', options.minutes, 'and updateTime:', options.updateTime );
                            that.bindResetEvents();
                            that.init();
                        }
                    });
            },
            log: function() {
                if ( options.debug || options.force ) {
                    console.info.apply( console, arguments );
                }
            }
        };

    $.extend({
        /**
         * Show overlay for updated homepage
         * @memberOf jQuery
         * @category Function
         */
        hpOverlay: function() {
            if ( !overlay.isLiveServer() && !options.debug && !options.force ) {
                overlay.log( 'Popup cancelled because not on live server.' );
                return;
            }

            var cookie = ZMO.cookieRead( 'overlaycanceled' );

            if ( options.force ) {
                overlay.show();
            } else if ( !ZMO.isMobileView() && cookie !== 1 ) {
                // only get config if there's no mobile view and cookie wasn't set
                overlay.log( 'Configure popup' );
                overlay.config();
            } else {
                overlay.log( 'Cookie present or mobile view, dropout.' );
            }
        }
    });

})( jQuery, window, document, window.ZMO );

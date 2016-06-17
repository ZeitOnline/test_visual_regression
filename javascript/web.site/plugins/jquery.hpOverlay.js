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

(function( $, window, document, Zeit ) {
    'use strict';

    // options may be overwritten by hpoverlay.config.js
    var options = {
            cookieTimeInDays: 1.5,
            endpoint: location.protocol + '//' + location.host + '/json_update_time/index',
            config: Zeit.jsconfHost + '/hpoverlay.config.js',
            minutes: 5,
            isOn: true,
            updateTime: 1,
            debug: location.search.indexOf( 'debug-popover' ) !== -1,
            force: location.search.indexOf( 'force-popover' ) !== -1
        },
        // define overlay object
        overlay = {
            wrapper: null,
            page: null,
            activeElement: null,
            initialized: false,
            timer: false,
            timestamp: null,
            visible: false,
            show: function() {
                if ( this.wrapper.not( ':visible' ) ) {
                    // show wrapper
                    this.wrapper.show();
                    this.wrapper.removeAttr( 'aria-hidden' );

                    // hide page body for a11y users
                    this.page.attr( 'aria-hidden', 'true' );

                    // trigger fake "appear" event
                    $( '#overlay-tracker' ).trigger( 'click' );
                }

                // set state
                this.visible = true;

                // save last focused element
                this.activeElement = document.activeElement;

                // fade everything in
                this.wrapper.find( '.overlay' ).fadeIn();
                this.wrapper.find( '.overlay__dialog' ).show();
                this.wrapper.find( '.overlay__button' ).focus();

                // bind events
                this.bindEvents();

                $( document ).off( '.modal' );
            },
            cancel: function() {
                // action when cancel was clicked
                window.clearTimeout( this.timer );

                // hide content
                this.wrapper.find( '.overlay, .overlay__dialog' ).hide();

                // show wrapper
                this.wrapper.hide();
                this.wrapper.attr( 'aria-hidden', 'true' );

                // show page body for a11y users
                this.page.removeAttr( 'aria-hidden' );

                // set state
                this.visible = false;

                // write cookie
                Zeit.cookieCreate( 'overlaycanceled', 'canceled', options.cookieTimeInDays, '' );

                // restore last focused element
                if ( this.activeElement ) {
                    this.activeElement.focus();
                }

                // unbind events
                this.unbindEvents();

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

                // proxy current context
                var that = this;

                // cancel button
                $( document ).on( 'click.hpoverlay', '.overlay__button', function( event ) {
                    event.preventDefault();
                    that.cancel();
                } );

                // reload
                $( document ).on( 'click.hpoverlay', '.overlay, .overlay__text-button', function( event ) {
                    event.preventDefault();
                    that.reload();
                } );

                // escape key
                $( window ).on( 'keyup.hpoverlay', function( event ) {
                    if ( event.which === 27 ) {
                        that.reload();
                    }
                } );

                // focus
                $( document ).on( 'focus.hpoverlay', 'body', function( event ) {
                    if ( that.visible && that.wrapper.find( event.target ).length === 0 ) {
                        that.wrapper.find( '.overlay__button' ).focus();
                    }
                } );

                this.initialized = true;
            },
            unbindEvents: function() {
                $( window ).off( '.hpoverlay' );
                $( document ).off( '.hpoverlay' );
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

                // clear timer
                if ( this.timer ) {
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

            var cookie = Zeit.cookieRead( 'overlaycanceled' );

            // Setup elements
            overlay.wrapper = $( '#overlay-wrapper' );
            overlay.page = $( 'body > .page' );

            if ( options.force ) {
                overlay.show();
            } else if ( !Zeit.isMobileView() && cookie !== 'canceled' ) {
                // only get config if there's no mobile view and cookie wasn't set
                overlay.log( 'Configure popup' );
                overlay.config();
            } else {
                overlay.log( 'Cookie present or mobile view, dropout.' );
            }
        }
    });

})( jQuery, window, document, window.Zeit );

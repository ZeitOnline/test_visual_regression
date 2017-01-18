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
 * @version 1.0
 *
 * @requires ZEIT-Lib
 */

(function( $, window, document, Zeit ) {
    'use strict';

    var Overlay = function() {
        this.activeElement = null;
        this.cookieValue = Zeit.cookieRead( 'overlaycanceled' );
        this.initialized = false;
        this.interval = ( parseInt( Zeit.view.get( 'hp_overlay_interval' ), 10 ) || 120 ) * 1000;
        this.isLiveServer = /^(www\.)?zeit\.de$/.test( window.location.hostname );
        this.options = {
            cookieTimeInDays: 1.5,
            debug: location.search.indexOf( 'debug-popover' ) !== -1,
            endpoint: location.protocol + '//' + location.host + '/json_update_time/index',
            force: location.search.indexOf( 'force-popover' ) !== -1,
            prevent: location.search.indexOf( 'prevent-popover' ) !== -1,
            resetInterval: 1000
        };
        this.page = $( 'body > .page' );
        this.timer = false;
        this.timestamp = null;
        this.visible = false;
        this.wrapper = $( '#overlay-wrapper' );

        this.init();
    };

    // start or restart popover process
    Overlay.prototype.init = function() {
        var that = this;
        if ( ( !this.isLiveServer && !this.options.debug && !this.options.force ) || this.options.prevent ) {
            this.log( 'Overlay cancelled by option.' );
            return;
        }
        if ( Zeit.isMobileView() || this.cookieValue === 'canceled' ) {
            this.log( 'Overlay canceled by breakpoint or cookie.' );
            return;
        }
        if ( this.options.force ) {
            this.log( 'Show overlay forced by option.' );
            this.show();
            return;
        }
        // look for keystrokes etc. only in active document
        if ( !document.hidden ) {
            this.bindResetEvents();
        }
        document.addEventListener( 'visibilitychange', function() {
            if ( document.hidden ) {
                that.log( 'document is hidden' );
                that.unbindResetEvents();
            } else {
                that.log( 'document is visible' );
                that.bindResetEvents();
                // always fetch if come back from hidden state
                that.fetchData();
            }
        });
        this.fetchData();
    };

    // log helper
    Overlay.prototype.log = function() {
        if ( this.options.debug || this.options.force || this.options.prevent ) {
            console.info.apply( console, arguments );
        }
    };

    // show overlay
    Overlay.prototype.show = function() {
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
    };

    // reset event binding
    Overlay.prototype.bindResetEvents = function() {
        // bind events to reset timer, need to debounce at least scroll and mousemove event
        var that = this;
        $( document ).on( 'keypress.modal scroll.modal click.modal mousemove.modal', $.debounce( function() {
            that.setTimeout();
        }, that.options.resetInterval ));
    };

    // reset event unbinding
    Overlay.prototype.unbindResetEvents = function() {
        $( document ).off( '.modal' );
    };

    // setTimeout if needed
    Overlay.prototype.setTimeout = function( time ) {
        var that = this,
            interval = time || this.interval;

        // clear timer
        if ( this.timer ) {
            window.clearTimeout( this.timer );
        }

        // start new timer
        if ( !this.visible ) {
            this.timer = window.setTimeout( function() { that.fetchData(); }, interval  );
            this.log( 'New timer started for ' + interval / 1000 / 60 + ' minutes' );
        }
    };

    // get the actual timestamp of page and check against prior data
    Overlay.prototype.fetchData = function() {
        // data is only fetched if document is visible
        if ( !document.hidden ) {
            var that = this;
            $.ajax( that.options.endpoint, { dataType: 'json' } ).done( function( data ) {
                that.log( 'Done: old timestamp: ' + that.timestamp + ', new timestamp: ' + data.last_published_semantic );
                if ( !that.timestamp ) {
                    that.timestamp = data.last_published_semantic;
                }
                if ( data.last_published_semantic && that.timestamp !== data.last_published_semantic ) {
                    // set timestamp here? was not in the old version though…
                    that.log( 'Show overlay b/c page was updated.' );
                    that.show();
                } else {
                    that.log( 'No update found, restarting timer.' );
                    that.setTimeout();
                }
            }).fail( function() {
                that.setTimeout();
            });
        }
    };

    // action when cancel was clicked
    Overlay.prototype.cancel = function() {
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
        this.cookieValue = 'canceled';
        Zeit.cookieCreate( 'overlaycanceled', 'canceled', this.options.cookieTimeInDays, '' );
        // restore last focused element
        if ( this.activeElement ) {
            this.activeElement.focus();
        }
        // unbind events
        this.unbindEvents();
        this.log( 'Refresh page cancelled' );
    };

    // action when reload button or overlay was clicked
    Overlay.prototype.reload = function() {
        window.location.reload();
    };

    // event binding
    Overlay.prototype.bindEvents = function() {
        if ( this.initialized ) {
            return;
        }
        // proxy current context
        var that = this;
        // cancel button
        $( document ).on( 'click.hpoverlay', '.overlay__text-button', function( event ) {
            event.preventDefault();
            that.cancel();
        } );
        // reload
        $( document ).on( 'click.hpoverlay', '.overlay, .overlay__button', function( event ) {
            event.preventDefault();
            that.reload();
        } );
        // escape key
        $( window ).on( 'keyup.hpoverlay', function( event ) {
            if ( event.which === 27 ) {
                that.cancel();
            }
        } );
        // focus
        $( document ).on( 'focus.hpoverlay', 'body', function( event ) {
            if ( that.visible && that.wrapper.find( event.target ).length === 0 ) {
                that.wrapper.find( '.overlay__button' ).focus();
            }
        } );
        this.initialized = true;
    };

    // event unbinding
    Overlay.prototype.unbindEvents = function() {
        $( window ).off( '.hpoverlay' );
        $( document ).off( '.hpoverlay' );
    };

    // jquery plugin
    $.extend({
        hpOverlay: function() {
            if ( Zeit.toggles.get( 'hp_overlay' ) ) {
                new Overlay();
            }
        }
    });

})( jQuery, window, document, window.Zeit );

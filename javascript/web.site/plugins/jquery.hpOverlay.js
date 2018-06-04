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
 * @version 1.01
 *
 * @requires ZEIT-Lib
 */

( function( $, window, document, Zeit ) {
    'use strict';

    function Overlay() {
        this.activeElement = null;
        this.cookieValue = Zeit.cookieRead( 'overlaycanceled' );
        this.initialized = false;
        this.interval = ( parseInt( Zeit.hpOverlay.interval, 10 ) || 120 ) * 1000;
        this.isLiveServer = /^(www\.)?zeit\.de$/.test( window.location.hostname );
        this.configuredProtocol = window.Zeit.toggles.https ? 'https:' : window.location.protocol;
        this.options = {
            cookieTimeInDays: 1.5,
            debug: location.href.indexOf( 'debug-popover' ) !== -1,
            endpoint: '//' + location.host + '/json/update-time/index',
            force: location.href.indexOf( 'force-popover' ) !== -1,
            prevent: location.href.indexOf( 'prevent-popover' ) !== -1,
            resetInterval: 1000
        };
        this.page = $( 'body > .page' );
        this.timer = false;
        this.timestamp = null;
        this.visible = false;
        this.wrapper = $( '#overlay-wrapper' );
        this.visibilityListener = null;
        this.init();
    }

    var visibilityListener = function() {
        if ( document.hidden ) {
            this.log( 'document is hidden' );
            this.unbindResetEvents();
        } else {
            this.log( 'document is visible' );
            this.bindResetEvents();
            // always fetch if come back from hidden state
            this.fetchData();
        }
    };

    // start or restart popover process
    Overlay.prototype.init = function() {
        if ( ( !this.isLiveServer && !this.options.debug && !this.options.force ) || this.options.prevent ) {
            this.log( 'Overlay cancelled by option.' );
            return;
        }
        if ( Zeit.isMobileView() || this.cookieValue === 'canceled' || Zeit.isWrapped ) {
            this.log( 'Overlay canceled by breakpoint, app or cookie.' );
            return;
        }
        // look for keystrokes etc. only in active document
        if ( !document.hidden ) {
            this.bindResetEvents();
        }
        // bind this on runtime to make it revokable
        this.visibilityListener = visibilityListener.bind( this );
        document.addEventListener( 'visibilitychange', this.visibilityListener );
        // add Podcast Event Listener
        this.addPostMessageEventListener();
        // fetchData initially
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
        $( document ).on( 'keypress.modal scroll.modal click.modal mousemove.modal', Zeit.debounce( function() {
            that.setTimeout();
        }, that.options.resetInterval ) );
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
            this.timer = window.setTimeout( function() {
                that.fetchData();
            }, interval );
            this.log( 'New timer started for ' + interval / 1000 / 60 + ' minutes' );
        }
    };

    // get the actual timestamp of page and check against prior data
    Overlay.prototype.fetchData = function() {
        this.log( 'fetchData started' );
        // force display of popover
        if ( this.options.force ) {
            this.log( 'Show overlay forced by option.' );
            this.show();
            return;
        }
        // data is only fetched if document is visible
        if ( !document.hidden ) {
            var that = this;
            $.ajax( that.configuredProtocol + that.options.endpoint, { dataType: 'json' }).done( function( data ) {
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
        this.addCancelCookie();
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
        window.scrollTo( 0, 0 );
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
        });
        // reload
        $( document ).on( 'click.hpoverlay', '.overlay, .overlay__button', function( event ) {
            event.preventDefault();
            that.reload();
        });
        // escape key
        $( window ).on( 'keyup.hpoverlay', function( event ) {
            if ( event.which === 27 ) {
                that.cancel();
            }
        });
        // focus
        $( document ).on( 'focus.hpoverlay', 'body', function( event ) {
            if ( that.visible && that.wrapper.find( event.target ).length === 0 ) {
                that.wrapper.find( '.overlay__button' ).focus();
            }
        });
        this.initialized = true;
    };

    // event unbinding
    Overlay.prototype.unbindEvents = function() {
        $( window ).off( '.hpoverlay' );
        $( document ).off( '.hpoverlay' );
        document.removeEventListener( 'visibilitychange', this.visibilityListener );
    };

    Overlay.prototype.sendPodcastPlayEventPostMessage = function() {
        // send postMessage with value play to get the message once the player starts
        $( '.podigee-podcast-player' ).each(
            function() {
                $( this ).context.contentWindow.postMessage(
                    JSON.stringify({
                        context: 'player.js',
                        version: 'version',
                        method: 'addEventListener',
                        value: 'play'
                    }),
                    '*'
                );
            }
        );
    };

    Overlay.prototype.listenToPostMessages = function() {
        var that = this;
        window.addEventListener( 'message', function( event ) {
            if ( that.cookieValue === 'canceled' ) {
                return;
            }
            var data =  JSON.parse( event.data );
            var matches = false;
            // quiz
            if ( data.name === 'quiz' && data.message === 'started' ) {
                matches = true;
            }
            // podcast
            if ( data.context === 'player.js' && data.event === 'play' ) {
                matches = true;
            }

            if ( matches ) {
                that.addCancelCookie();
                that.log( 'Added Cookie' );
            }
        }, false );
    };

    Overlay.prototype.addPostMessageEventListener = function() {
        this.sendPodcastPlayEventPostMessage();
        this.listenToPostMessages();
    };

    Overlay.prototype.addCancelCookie = function() {
        this.cookieValue = 'canceled';
        Zeit.cookieCreate( 'overlaycanceled', this.cookieValue, this.options.cookieTimeInDays, '' );
    };

    // jquery plugin
    $.extend({
        hpOverlay: function() {
            if ( Zeit.hpOverlay.active ) {
                new Overlay();
            }
        }
    });

})( jQuery, window, document, window.Zeit );

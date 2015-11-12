// jscs:disable requireCamelCaseOrUpperCaseIdentifiers
/**
 * @fileOverview API for asynchronely reload ads on webpages
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
define( [ 'jquery' ], function( $ ) {

    var debug = location.search.indexOf( 'debug-adreload' ) !== -1,
    configUrl = window.ZMO.jsconfHost + '/config_adreload.json',
    config = false,
    timer = {},
    /**
     * logging helper - wraps if debug --> console.log
     * @return {void}
     */
    log = function() {
        if ( location.search.indexOf( 'debug-adreload' ) !== -1 ) {
            var args = Array.prototype.slice.call( arguments );
            // just one argument which is a string
            if ( args.length === 1 && typeof args[0] === 'string' ) {
                console.log( args.toString() );
            } else {
                // all other cases
                console.log( args );
            }
        }
    },
    /**
     * check timer and click interval
     * @param  {object} myconfig configuration section read from json before
     * @return {bool}
     */
    checkClickCount = function( myconfig ) {
        // do we need a timer?
        if ( typeof myconfig.time !== 'undefined' && myconfig.time > 0 ) {
            // timer not set
            if ( typeof timer[myconfig.name] !== 'undefined' && timer[myconfig.name] === true ) {
                // do not count while timer is set
                if ( debug ) { console.debug( 'TIMER läuft noch' ); }
                return false;
            } else {
                // set timer
                window.setTimeout( function() {
                    timer[myconfig.name] = false;
                }, myconfig.time );
                timer[myconfig.name] = true;
                // extra
                return clickCount( myconfig );
            }
        } else {
            return clickCount( myconfig );
        }
    },
    clickCount = function( myconfig ) {
        // load on every click
        if ( myconfig.interval < 2 ) {
            if ( debug ) { console.debug( 'direct click' ); }
            return true;
        }
        // load cause max reached
        if ( $( 'body' ).data( myconfig.name ) + 1 === myconfig.interval ) {
            if ( debug ) { console.debug( 'max click' ); }
            return true;
        }  else {
            if ( $( 'body' ).data( myconfig.name ) ) {
                if ( debug ) { console.debug( 'add up clicks' ); }
                $( 'body' ).data( myconfig.name, $( 'body' ).data( myconfig.name ) + 1 );
            } else {
                if ( debug ) { console.debug( 'first click' ); }
                $( 'body' ).data( myconfig.name, 1 );
            }
            return false;
        }
    },
    /**
     * initialize a new counting mandator by checking id against configuration
     * @return {bool}   return state when ready
     */
    loadConfig = function() {
        return $.ajax( configUrl, { dataType: 'json' } );
    },
    interaction = function( event, sender, message ) {
        // check config if sender is registered
        if ( typeof config[ sender ] === 'undefined' ) { return; }
        var myconfig = config[ sender ];
        // check if slug and pagetype match
        if (
            window.location.pathname.indexOf( myconfig.slug ) < 0 ||
            $.inArray( window.ZMO.view.type, myconfig.pagetypes ) < 0
        ) { return; }
        if ( checkClickCount( myconfig ) ) {
            // reload Ads
            if ( typeof window.IQD_ReloadHandle !== 'undefined' ) {
                if ( debug ) { console.debug( 'adReload emitted' ); }
                window.IQD_ReloadHandle();
            }
            // emit webtrekk PI
            if ( typeof window.wt !== 'undefined' ) {
                if ( debug ) { console.debug( 'webtrekk emitted' ); }
                window.wt.sendinfo();
            }
            // emit IVW PI
            if ( typeof window.iom !== 'undefined' && typeof window.iam_data !== 'undefined' ) {
                if ( debug ) { console.debug( 'ivw emitted' ); }
                window.iom.c( window.iam_data, 1 );
            }
        }
    },
    /**
     * channel filtered window.messages to interaction api
     * @param  {object} event DOM event
     * @return {void}
     */
    message = function( event ) {
        var messageData, sender, message;
        try {
            messageData = JSON.parse( event.originalEvent.data );
        } catch ( e ) {
            return;
        }
        if ( typeof messageData.sender !== 'string' || typeof messageData.message !== 'string' ) {
            console.error( 'messageData not completely set' );
            return;
        }
        $( window ).trigger( 'interaction.adreload.z', [ sender, message ]);
    };

    return {
        init: function() {
            // load configuration
            var inits = loadConfig();
            inits.done( function() {
                config = inits.responseJSON;
                // add eventlistener
                $( window ).on( 'interaction.adreload.z', interaction );
                // listen to window.messages for channel interactions
                $( window ).on( 'message', message );
            });
            // on page unload unbind all at unload to prevent memory leaks
            $( window ).on( 'unload', function( event ) {
                $( window ).off( 'adreload' );
            });
        }
    };
});

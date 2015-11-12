// jscs:disable requireCamelCaseOrUpperCaseIdentifiers
/**
 * @fileOverview API for asynchronely reload ads on webpages
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
define( [ 'jquery' ], function( $ ) {

    var configUrl = window.ZMO.jsconfHost + '/config_adreload.json',
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
    /**
     * check against the interaction interval
     * @param  {object} myconfig configuration section read from json before
     * @return {bool}
     */
    clickCount = function( myconfig ) {
        // load on every click
        if ( myconfig.interval < 2 ) {
            log( 'direct click' );
            return true;
        }
        // load cause max reached
        if ( $( 'body' ).data( myconfig.name ) + 1 === myconfig.interval ) {
            log( 'max click' );
            $( 'body' ).removeData( myconfig.name );
            return true;
        }  else {
            if ( $( 'body' ).data( myconfig.name ) ) {
                log( 'add up clicks' );
                $( 'body' ).data( myconfig.name, $( 'body' ).data( myconfig.name ) + 1 );
            } else {
                log( 'first click' );
                $( 'body' ).data( myconfig.name, 1 );
            }
            return false;
        }
    },
    /**
     * load configuration from json file
     * @return {object} ajax promise
     */
    loadConfig = function() {
        return $.ajax( configUrl, { dataType: 'json' } );
    },
    /**
     * interaction event
     * @param  {object} event   DOM event object
     * @param  {string} name  interaction emmitter name
     * @param  {string} message message field of the request
     * @return {void}
     */
    interaction = function( event, name, message ) {
        // check config if name is registered
        var myconfig;
        try {
            myconfig = config[ name ];
            log( myconfig );
        } catch ( e ) {
            log( 'error', e );
            return;
        }
        // check if slug and pagetype match
        if (
            window.location.pathname.indexOf( myconfig.slug ) < 0 ||
            $.inArray( window.ZMO.view.type, myconfig.pagetypes ) < 0
        ) { return; }
        if ( checkClickCount( myconfig ) ) {
            // reload Ads
            if ( typeof window.IQD_ReloadHandle !== 'undefined' ) {
                log( 'adReload emitted' );
                window.IQD_ReloadHandle();
            }
            // emit webtrekk PI
            if ( typeof window.wt !== 'undefined' ) {
                log( 'webtrekk emitted' );
                window.wt.sendinfo();
            }
            // emit IVW PI
            if ( typeof window.iom !== 'undefined' && typeof window.iam_data !== 'undefined' ) {
                log( 'ivw emitted' );
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
        var messageData, message;
        log( 'message: ', event );
        try {
            messageData = JSON.parse( event.originalEvent.data );
        } catch ( e ) {
            log( 'error', e );
            return;
        }
        if ( typeof messageData.name !== 'string' || event.originalEvent.origin !== config[messageData.name].origin ) {
            log( 'error', 'messageData not correctly set' );
            return;
        }
        $( window ).trigger( 'interaction.adreload.z', [ messageData.name, messageData.message ] );
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

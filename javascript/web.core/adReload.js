/**
 * @fileOverview API for asynchronely reload ads on webpages
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
define([ 'jquery', 'web.core/zeit' ], function( $, Zeit ) {

    var configUrl = Zeit.jsconfHost + '/config_adreload.json',
        config = false,
        timer = {},
        clickCounter = [];

    /**
     * logging helper - wraps if debug --> console.log
     * @return {void}
     */
    function log() {
        if ( window.location.search.indexOf( 'debug-adreload' ) !== -1 ) {
            console.log.apply( console, arguments );
        }
    }

    /**
     * test if a supplied origin fits into the configured list of origins
     * be backward compatible to older form of string
     * @param  {string|array}   configuredOrigin list of origins from the config
     * @param  {object}  event  message event object
     * @return {Boolean}
     */
    function isValidOrigin( configuredOrigin, event ) {
        configuredOrigin  = typeof configuredOrigin === 'string' ? [ configuredOrigin ] : configuredOrigin;
        return $.inArray( event.originalEvent.origin, configuredOrigin ) > -1;
    }

    /**
     * check against the interaction interval
     * @param  {object} myconfig configuration section read from json before
     * @return {bool}
     */
    function clickCount( myconfig ) {
        // load on every click
        if ( myconfig.interval < 2 ) {
            log( 'direct click' );
            return true;
        }

        // consecutive events
        if ( clickCounter[ myconfig.name ]) {
            // gained configured interval
            if ( ++clickCounter[ myconfig.name ] % myconfig.interval === 0 ) {
                log( 'max click' );
                return true;
            } else {
                log( 'add up clicks' );
            }
        }  else {
            log( 'first click' );
            clickCounter[ myconfig.name ] = 1;
        }

        return false;
    }

    /**
     * check timer and click interval
     * @param  {object} myconfig configuration section read from json before
     * @return {bool}
     */
    function checkClickCount( myconfig ) {
        // do we need a timer?
        if ( typeof myconfig.time !== 'undefined' && myconfig.time > 0 ) {
            var now = $.now();

            if ( timer[ myconfig.name ] > now ) {
                // do not count if timer is set in the future
                return false;
            } else {
                // set timer
                timer[ myconfig.name ] = now + myconfig.time;
                // extra
                return clickCount( myconfig );
            }
        } else {
            return clickCount( myconfig );
        }
    }

    /**
     * load configuration from json file
     * @return {object} ajax promise
     */
    function loadConfig() {
        return $.ajax( configUrl, { dataType: 'json' });
    }

    /**
     * interaction event
     * @param  {object} event   DOM event object
     * @param  {string} name  interaction emmitter name
     * @return {void}
     */
    function interaction( event, name ) {
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
            $.inArray( Zeit.view.type, myconfig.pagetypes ) < 0
        ) {
            return;
        }

        if ( checkClickCount( myconfig ) ) {
            // reload Ads
            if ( typeof window.IQD_ReloadHandle === 'function' ) {
                log( 'adReload emitted' );
                window.IQD_ReloadHandle();

                // emit webtrekk PI
                if ( 'wt' in window && typeof window.wt.sendinfo === 'function' ) {
                    log( 'webtrekk emitted' );
                    window.wt.sendinfo();
                }

                // emit IVW PI
                if ( 'iom' in window && typeof window.iom.h === 'function' && typeof window.iam_data !== 'undefined' ) {
                    log( 'ivw emitted' );
                    window.iom.h( window.iam_data, 1 );
                }
            }
        }
    }

    /**
     * channel filtered window.messages to interaction api
     * @param  {object} event DOM event
     * @return {void}
     */
    function message( event ) {
        var messageData;

        if ( typeof event.originalEvent.data  !== 'string' ) {
            return;
        }

        // Avoid JSON-parsing of messages which are not JSON
        if ( event.originalEvent.data.indexOf( '{' ) !== 0 ) {
            return;
        }

        try {
            messageData = JSON.parse( event.originalEvent.data );
        } catch ( e ) {
            log( 'error', e );
            return;
        }

        if ( typeof messageData.name !== 'string' ||
                typeof config[ messageData.name ] === 'undefined' ||
                !isValidOrigin( config[ messageData.name ].origin, event ) ) {
            log( 'error', 'messageData not correctly set' );
            return;
        }

        $( window ).trigger( 'interaction.adreload.z', [ messageData.name, messageData.message ]);
    }

    return {
        init: function() {
            log( 'debug-adreload started' );
            // load configuration
            var inits = loadConfig();
            inits.done( function() {
                config = inits.responseJSON;
                // add eventlistener
                $( window ).on( 'interaction.adreload.z', interaction );
                // listen to window.messages for channel interactions
                $( window ).on( 'message', message );
            });
            inits.fail( function( jqXHR, textStatus, errorThrown ) {
                log( 'error', errorThrown );
            });
            // on page unload unbind all at unload to prevent memory leaks
            $( window ).on( 'unload', function() {
                $( window ).off( 'adreload' );
            });
        }
    };
});

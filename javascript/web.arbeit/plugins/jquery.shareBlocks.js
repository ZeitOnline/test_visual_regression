/**
 * @fileOverview jQuery Plugin for calling the Sharebert feature on
 * article blocks.
 * @author thomas.puppe@zeit.de
 * @version 0.1
 */
( function( $ ) {

    'use strict';

    var debugMode = location.hash.indexOf( 'debug-shareblocks' ) > -1,
        rootElement,
        labelElement,
        itemsElement;

    function log() {
        if ( debugMode ) {
            var args = Array.prototype.slice.call( arguments );
            console.log.apply( console, args );
        }
    }

    /**
     * Initializes instance variables.
     *
     * @constructor
     */
    function ShareBlock( rootElement ) {
        log( 'ShareBlock()' ); // REMOVE
        this.rootElement = rootElement;
        this.init();
    }

    ShareBlock.prototype.init = function() {
        this.labelElement = this.rootElement.querySelector( '.js-shareblock__label' );
        this.itemsElement = this.rootElement.querySelector( '.js-shareblock__items' );

        this.itemsElement.style.display = 'none';
        this.labelElement.addEventListener( 'click', this.clickEvent );
    };

    ShareBlock.prototype.clickEvent = function( event ) {
        event.preventDefault();

        // getSharebertData().then(exchangeLink())
        // slideInTheButtons();

        window.console.debug( this.rootElement );

        this.itemsElement.style.display = 'inline-block'; // TODO: use classes/aria
    };


    var getSharebertData = function( sharebertShotUrl, sharebertRedirectUrl ) {
        return new window.Promise( function( resolve, reject ) {

            var metaData = {
                'title': document.title,
                'description': document.querySelector( 'meta[name=description]' ).getAttribute( 'content' )
            };
            var myData = {
                'target_url': sharebertShotUrl,
                'meta_data': metaData,
                'redirect_to': sharebertRedirectUrl
            };

            var xhr = new XMLHttpRequest();
            xhr.open( 'POST', 'http://share.zeit.de/-/apps/twitter-quote/shots' );
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
            xhr.setRequestHeader( 'Content-Type', 'application/json; charset=utf-8' );
            xhr.send( JSON.stringify( myData ) );

        });
    };

    var share = function( event ) {

        event.preventDefault();

        // getSharebertData().then(exchangeLink())
        // slideInTheButtons();

        itemsElement.style.display = 'inline-block'; // TODO: use classes/aria

        getSharebertData();

        /*
        // Lösung: innerhalb von init() oder share() die Daten halten. Nicht im Plugin.
        var $elem = $( event.target ).closest( '.js-shareblock' );
        var sharebertRedirectUrl = $elem.data( 'sharebert-redirect-url' );
        var sharebertShotUrl = $elem.data( 'sharebert-screenshot-target' );
        // for testing locally (Sharebert cannot reach your localhost), use nginx or:
        // sharebertShotUrl = 'http://live0.zeit.de/twitter-quote/?quote=Das%20hat%20alles%20keinen%20Gin.';
        log( 'sharebertRedirectUrl: ' + sharebertRedirectUrl );
        log( 'sharebertShotUrl: ' + sharebertShotUrl );

        getSharebertData( sharebertShotUrl, sharebertRedirectUrl )
            .then( function( response ) {
                log( 'SUCCESS, got URL:' + response.src_url );
                var shareLink = 'https://twitter.com/intent/tweet?text=' +
                    encodeURIComponent( response.src_url );

                // window.open() is popup-blocked, so we change the link and trigger a click
                var elem = $elem[ 0 ];
                elem.removeEventListener( 'click', share );
                elem.setAttribute( 'href', shareLink );
                elem.click();

            }, function( error ) {
                log( 'error', error );
            });

        $elem.blur();
        */
    };

    function initShareBlocks() {
        if ( !window.fuck ) {
            return;
        }
        labelElement = rootElement.querySelector( '.js-shareblock__label' );
        itemsElement = rootElement.querySelector( '.js-shareblock__items' );

        itemsElement.style.display = 'none';
        labelElement.addEventListener( 'click', share );
    }

    $.fn.shareBlocks = function() {

        // Promises working since iOS Safari8, Android Browser 4.4.4, Chrome+FF+Opera+Edge.
        // Promise not working in IE 11.
        // Fallback is the regular share URL
        // That way, we can also use XMLHttpRequest with a JSON response.
        if ( !window.Promise ) {
            return;
        }

        return this.each( function() {
            new ShareBlock( this );
            initShareBlocks(); // REMOVE
        });
    };
})( jQuery );

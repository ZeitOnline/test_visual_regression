/**
 * @fileOverview jQuery Plugin for calling the Sharebert feature on
 * article blocks.
 * @author thomas.puppe@zeit.de
 * @version 0.1
 */
( function( $, Zeit ) {

    'use strict';

    var settings,
        defaults = {
            sharebertUrl: 'http://share.zeit.de/-/apps/twitter-quote/shots',
            duration: 200
        },
        debugMode = location.hash.indexOf( 'debug-shareblocks' ) > -1;

    function log() {
        if ( debugMode ) {
            var args = Array.prototype.slice.call( arguments );
            console.log.apply( console, args );
        }
    }

    function openShareWindow( url ) {
        // TODO: PopUp ist halt doof.
        // Alternative, bzw auf jeden Fall tun: Link umschreiben, Clickhandler entfernen.
        // Kann man feststellen ob das Fenster öffnet? Und, falls nicht, den Link öffnen?
        // Ginge ein iFrame?
        log( 'OPEN share window ' + url );
        window.open( url, '', 'menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=300,width=600' );
    }

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

            // The jQuery approach sends two requests: OPTIONS + POST.
            $.ajax({
                url: settings.sharebertUrl,
                type: 'POST',
                data: JSON.stringify( myData ),
                processData: false,
                contentType: 'application/json; charset=utf-8',
                dataType: 'json'
            }).done( function( data ) {
                log( 'SUCCESS', data );
                resolve( data );
            }).fail( function( jqXHR, textStatus, errorThrown ) {
                var errorMessage = 'Leider ist ein Fehler aufgetreten, bitte versuchen Sie es später noch einmal.';
                log( 'ERROR', errorMessage, textStatus, errorThrown );
                reject( Error( errorMessage ) );
            });

            // The native approach does not work, because I dont get the POST data formatted correctly.
            // Server responds with Error 400
            // {"status": "error", "errors": [{"location": "body",
            // "description": "\"b'[object Object]'\" is not a mapping type: Does not implement dict-like functionality.", "name": ""}]}
            /*
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
            xhr.setRequestHeader( 'Content-Type', myData.contentType );
            xhr.send( myData );
            */
        });
    };

    var share = function( event ) {

        event.preventDefault();

        // Lösung: innerhalb von init() oder share() die Daten halten. Nicht im Plugin.
        var $elem = $( event.target ).closest( '.js-shareblock' );
        var sharebertRedirectUrl = $elem.data( 'sharebert-redirect-url' );
        var sharebertShotUrl = $elem.data( 'sharebert-screenshot-target' );
        log( 'sharebertRedirectUrl: ' + sharebertRedirectUrl );
        log( 'sharebertShotUrl: ' + sharebertShotUrl );

        getSharebertData( sharebertShotUrl, sharebertRedirectUrl )
            .then( function( response ) {
                log( 'SUCCESS, got URL:' + response.src_url );
                var shareLink = 'https://twitter.com/intent/tweet?text=' +
                    encodeURIComponent( response.src_url );
                openShareWindow( shareLink );
            }, function( error ) {
                log( 'error', error );
            });

        $elem.blur();
    };

    function initShareBlocks( element ) {
        log( 'initialize click event on ' + element );
        element.addEventListener( 'click', share );
    }

    $.fn.shareBlocks = function( options ) {

        // Promises working since iOS Safari8, Android Browser 4.4.4, Chrome+FF+Opera+Edge.
        // Promise not working in IE 11.
        // Fallback is the regular share URL
        // That way, we can also use XMLHttpRequest with a JSON response.
        if ( !window.Promise ) {
            return;
        }

        settings = $.extend({}, defaults, options );

        log( 'setup shareBlocks with ' + Zeit + ' and ' + settings );

        return this.each( function() {
            initShareBlocks( this );
        });
    };
})( jQuery, window.Zeit );

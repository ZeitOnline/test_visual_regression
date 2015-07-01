/**
* @fileOverview Module for the homepage gallery teaser (shuffle loading)
* @version  0.1
*/
/**
* Module for the homepage gallery teaser (shuffle loading)
* @module galleryTeaser
*/
define([ 'jquery' ], function( $ ) {

    /**
    * galleryTeaser.js: load and inject teasers
    * @function loadGalleryTeasers
    */
    var loadGalleryTeasers = function( event ) {

        var $eventTarget = $( event.target ),
            sourceUrl = $eventTarget.data( 'sourceurl' ),
            $galleryArea = $eventTarget.closest( '.cp-area--gallery' );

        if ( typeof sourceUrl !== 'string' || sourceUrl === '' ) {
            // TODO: wrap this shit, incuding the possibility to log it somewhere
            if ( typeof console === 'object' && typeof console.log === 'function' ) {
                console.log( 'Error with galleryTeaser.js ' +
                'reading sourceurl: "' + sourceUrl + '"' );
            }
            return false;
        }

        sourceUrl = sourceUrl.replace( '___JS-RANDOM___', Math.floor( Math.random() * 10 ) );

        $.get( sourceUrl, function( data ) {
            $galleryArea.replaceWith( data );
        });

        // TODO: Error Handling

        // $galleryArea.parent().load( sourceUrl, function( response, status, xhr ) {
        //     if ( status === 'error' ) {
        //         // TODO: wrap this shit, incuding the possibility to log it somewhere
        //         if ( typeof console === 'object' && typeof console.log === 'function' ) {
        //             console.log( 'Error with galleryTeaser.js loading from "' +
        //             sourceUrl + '": ' +
        //             xhr.status + ' ' + xhr.statusText );
        //         }
        //         return false;
        //     }
        // });
    },

    /**
    * galleryTeaser.js: register click event on button
    * @function init
    */
    init = function() {
        // register event handler
        $( '.cp-region--gallery' ).on( 'click', '.js-gallery-teaser-shuffle', loadGalleryTeasers );
    };

    return {
        init: init
    };

});

// TODO:
// - was, wenn mehrere Teaser-Groups auf einer Seite sind?

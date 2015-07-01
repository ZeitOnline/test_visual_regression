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
            $galleryArea,
            sourceUrl;

        $galleryArea = $eventTarget.closest( '.cp-area--gallery' );
        if ( typeof $galleryArea !== 'object' || $galleryArea.length === 0 ) {
            // OPTIMIZE: wrap this shit into a globally available module,
            // including the possibility to log it somewhere,
            // have debug mode (Konami Code FTW!), and so on.
            if ( typeof console === 'object' && typeof console.log === 'function' ) {
                console.log( 'Error with galleryTeaser.js, ' +
                'could not find $galleryArea for $eventTarget' );
            }
            return false;
        }

        sourceUrl = $eventTarget.data( 'sourceurl' );
        if ( typeof sourceUrl !== 'string' || sourceUrl === '' ) {
            // OPTIMIZE: wrap this shit into a globally available module,
            // including the possibility to log it somewhere,
            // have debug mode (Konami Code FTW!), and so on.
            if ( typeof console === 'object' && typeof console.log === 'function' ) {
                console.log( 'Error with galleryTeaser.js, ' +
                'reading sourceurl: "' + sourceUrl + '"' );
            }
            return false;
        }

        sourceUrl = sourceUrl.replace( '___JS-RANDOM___', Math.floor( Math.random() * 10 ) );

        $.get( sourceUrl, function( data ) {
            $galleryArea.replaceWith( data );
        } ).fail(function( errorObj ) {
            // OPTIMIZE: wrap this shit into a globally available module,
            // including the possibility to log it somewhere,
            // have debug mode (Konami Code FTW!), and so on.
            if ( typeof console === 'object' &&
                typeof console.log === 'function' &&
                typeof errorObj === 'object' &&
                typeof errorObj.statusText === 'string' ) {
                console.log( 'Error with galleryTeaser.js, ' +
                'loading new teasers: "' + errorObj.statusText + '"' );
            }
            // TODO: where to get the URL? We cannot traverse the area and find read-more, can we?
            window.location.href = '/foto/index';
            return false;
        });

    },

    /**
    * galleryTeaser.js: register click event on button
    * @function init
    */
    init = function() {
        $( '.js-gallery-teaser-shuffle' ).on( 'click', loadGalleryTeasers );
    };

    return {
        init: init
    };

});

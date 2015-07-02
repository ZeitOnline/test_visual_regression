/**
* @fileOverview Module for the homepage gallery teaser (shuffle loading)
* @version  0.1
*/
/**
* Module for the homepage gallery teaser (shuffle loading)
* @module galleryTeaser
*/
define([ 'jquery', 'web.core/images' ], function( $, images ) {

    /**
    * galleryTeaser.js: load and inject teasers
    * @function loadGalleryTeasers
    */
    var loadGalleryTeasers = function( event ) {

        var $this = $( this ),
            $galleryArea = $this.closest( '.cp-area--gallery' ),
            sourceUrl = $this.data( 'sourceurl' );

        if ( !$galleryArea.length || !sourceUrl ) {
            return false;
        }

        sourceUrl = sourceUrl.replace( '___JS-RANDOM___', Math.floor( Math.random() * 10 ) );

        $.get( sourceUrl, function( data ) {
            var selector = '.teaser-gallery-group__container',
                $data = $( data ),
                $teasers = $data.find( selector );

            images.scale( $galleryArea.find( selector ).html( $teasers.html() ) );
        } ).fail(function( errorObj ) {
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

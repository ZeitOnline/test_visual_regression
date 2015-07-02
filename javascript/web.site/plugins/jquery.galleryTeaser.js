/**
 * @fileOverview jQuery Plugin for the homepage gallery teaser (shuffle loading)
 * @author thomas.puppe@zeit.de
 * @version  0.1
 */
 define( [ 'jquery', 'web.core/images' ], function( $, images ) {
    (function( $, images ) {
        /**
        * See (http://jquery.com/)
        * @name jQuery
        * @alias $
        * @class jQuery Library
        * See the jQuery Library  (http://jquery.com/) for full details.  This just
        * documents the function and classes that are added to jQuery by this plug-in.
        */
        /**
        * See (http://jquery.com/)
        * @name fn
        * @class jQuery Library
        * See the jQuery Library  (http://jquery.com/) for full details.  This just
        * documents the function and classes that are added to jQuery by this plug-in.
        * @memberOf jQuery
        */
        /**
        * Loads and injects teasers into the "Fotogalerie Riegel" on CPs
        * @class loadGalleryTeasers
        * @memberOf jQuery.fn
        * @return {object} jQuery-Object for chaining
        */
        $.fn.loadGalleryTeasers = function() {

            /**
            * galleryTeaser.js: load and inject teasers
            * @function loadGalleryTeasers
            */
            var loadGalleryTeasers = function( event ) {

                var $this = $( this ),
                    $galleryArea = $this.closest( '.cp-area--gallery' ),
                    sourceUrl = $this.data( 'sourceurl' ),
                    fallbackUrl;

                if ( !$galleryArea.length || !sourceUrl ) {
                    return true;
                }

                sourceUrl = sourceUrl.replace( '___JS-RANDOM___', Math.floor( Math.random() * 10 ) );

                $.get( sourceUrl, function( data ) {
                    var selector = '.teaser-gallery-group__container',
                        $data = $( data ),
                        $teasers = $data.find( selector );

                    $galleryArea.find( selector ).replaceWith( $teasers );
                    images.scale( $teasers );
                } ).fail(function( ) {
                    fallbackUrl = $this.attr( 'href' );
                    if ( sourceUrl ) {
                        window.location.href = fallbackUrl;
                    }
                });

                return false;

            };

            return this.each( function() {
                $( this ).on( 'click', loadGalleryTeasers );
            });
        };
    })( jQuery, images );
} );

/**
 * @fileOverview jQuery Plugin for displaying image copyrights in footer
 * @author thomas.puppe@zeit.de
 * @version  0.1
 */
(function( $ ) {
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
    * toggle view of footer areas for mobile devices
    * @class extendFooter
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.imageCopyrightFooter = function() {

        var containerTemplate = '<div class="image-copyright-footer">' +
                '<div class="image-copyright-footer__container">' +
                '<h2 class="image-copyright-footer__headline">' +
                    'Bildrechte auf dieser Seite' +
                    '<span class="js-image-copyright-footer-close image-copyright-footer__close">schließen</span>' +
                '</h2>' +
                '___items___</div></div>',
            itemTemplate = '<div class="image-copyright-footer__item">' +
                '<img class="image-copyright-footer__item-image" src="___image___" />' +
                '<span class="image-copyright-footer__item-text">___name___</span>' +
                '</div>',
            initialized = false;

        function showImageCopyrightFooter( ) {

            if ( this.initialized ) {
                $( '.image-copyright-footer' ).show();
                return;
            }

            var $imagesWithCopyright = $( 'figure' ),
                imagesWithCopyrightLength = $imagesWithCopyright.length,
                i,
                wholeString,
                $currentImage,
                $currentCopyrightHolder,
                currentName,
                currentImageUrl;

            // TODO: This is too holprig!!
            for ( i = 0; i < imagesWithCopyrightLength; i++ ) {
                $currentImage = $imagesWithCopyright.eq( i );
                $currentCopyrightHolder = $currentImage.find( '*[itemprop=copyrightHolder]' );
                if ( $currentCopyrightHolder.length === 0 ) {
                    continue;
                }

                currentName = $currentCopyrightHolder.eq( 0 ).text();
                if ( currentName === '' ) {
                    continue;
                }

                currentImageUrl = $currentImage.find( 'img' ).eq( 0 ).attr( 'src' );
                wholeString += itemTemplate
                    .replace( '___name___', $currentCopyrightHolder.html() )
                    .replace( '___image___', currentImageUrl );
            }

            $( '.footer-links__button' ).eq( 0 ).before( containerTemplate.replace( '___items___', wholeString ) );

            $( '.js-image-copyright-footer-close' ).on( 'click', function( e ) {
                e.preventDefault();
                $( '.image-copyright-footer' ).hide();
            } );

            this.initialized = true;

        }

        return this.each( function() {
            $( this ).on( 'click', function( e ) {
                e.preventDefault();
                showImageCopyrightFooter( );
            } );

        });
    };
})( jQuery );

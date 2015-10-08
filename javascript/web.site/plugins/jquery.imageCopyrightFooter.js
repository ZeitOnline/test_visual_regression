/**
 * @fileOverview jQuery Plugin for extending footer
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

        var template = '<p>' +
            '<img class="image-copyright-footer__item-image" src="___image___" />' +
            '<span class="image-copyright-footer__item-text">___name___</span>' +
            '</p>';

        // TODO:
        // Alle Kommentare anpassen

        // toggle footer display
        function toggleImageCopyrightFooter( $button ) {

            // TODO: Performance
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
                wholeString += template
                    .replace( '___name___', currentName )
                    .replace( '___image___', currentImageUrl );
            }

            $button.append( wholeString );

            /*
            var $slides = $button.parent().nextAll( '.footer-publisher__row' ).add( '.footer-links__row' );

            $button.toggleClass( 'footer-publisher__more--expanded' );

            if ( $button.hasClass( 'footer-publisher__more--expanded' ) ) {
                $slides.slideDown({ duration: animationDuration });
                $button.text( 'Schließen' ).scrollIntoView({ duration: scrollDuration });
            } else {
                $slides.slideUp({ duration: animationDuration });
                $button.text( 'Mehr' );
            }
            */
        }

        return this.each( function() {
            var $button = $( this );

            $button.on( 'click', function( e ) {
                e.preventDefault();
                toggleImageCopyrightFooter( $button );
            } );
        });
    };
})( jQuery );

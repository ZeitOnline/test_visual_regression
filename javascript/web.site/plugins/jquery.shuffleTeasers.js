/**
 * @fileOverview jQuery Plugin for the homepage gallery teaser (shuffle loading)
 * @author thomas.puppe@zeit.de
 * @version  0.1
 */
define([ 'jquery', 'web.core/images' ], function( $, images ) {
    /**
    * shuffleTeasers.js: load and inject teasers
    * @function loadGalleryTeasers
    */
    function loadGalleryTeasers( event ) {

        var $this = $( this ),
            $galleryArea = $this.closest( '.cp-area' ),
            sourceUrl = $this.data( 'sourceurl' ),
            fallbackUrl;

        if ( !$galleryArea.length || !sourceUrl ) {
            return true;
        }

        $.get( sourceUrl, function( data ) {
            var selector = 'article[data-type="teaser"]',
                $data = $( data ),
                $teasers = $data.find( selector ),
                $shuffleButton = $galleryArea.find( '.js-bar-teaser-shuffle' ),
                duration = 400,
                nextPageSource = $data.find( '.js-bar-teaser-shuffle' ).data( 'sourceurl' );

            if ( $galleryArea.offset().top < document.documentElement.scrollTop ) {
                $galleryArea.velocity( 'scroll', duration );
            }

            if ( nextPageSource ) {
                $shuffleButton.data( 'sourceurl', nextPageSource );
            } else {
                $shuffleButton.velocity( { opacity: 0 }, { visibility: 'hidden' } );
            }

            $galleryArea.find( selector ).velocity( 'transition.slideLeftBigOut', {
                    duration: duration,
                    stagger: 50,
                    complete: function( elements ) {
                        $( elements ).parent().replaceWith( $teasers.parent() );
                        images.scale( $teasers );
                        $teasers.velocity( 'transition.slideRightBigIn', {
                            display: '', // remove the property altogether and return to previous display value from CSS
                            duration: duration,
                            stagger: 50
                        });
                    }
                });
        }).fail(function( ) {
            fallbackUrl = $this.attr( 'href' );
            if ( sourceUrl ) {
                window.location.href = fallbackUrl;
            }
        });

        return false;
    }

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
     * @class shuffleTeasers
     * @memberOf jQuery.fn
     * @return {object} jQuery-Object for chaining
     */
    $.fn.shuffleTeasers = function() {
        return this.on( 'click', loadGalleryTeasers );
    };
});

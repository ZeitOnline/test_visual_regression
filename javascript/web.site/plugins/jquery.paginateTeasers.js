/**
 * @fileOverview jQuery Plugin for the homepage gallery teaser (shuffle loading)
 * @author thomas.puppe@zeit.de
 * @version  0.1
 */
define([ 'jquery', 'web.core/images' ], function( $, images ) {

    var test = 'dummy',
        $this,
        $galleryArea,
        $allTeasers,
        $hiddenTeasers,
        $visibleTeasers,
        sourceUrl,
        fallbackUrl,
        slidingDuration = 400;

    /**
    * paginateTeasers.js: load and inject teasers
    * @function loadGalleryTeasers
    */
    function loadGalleryTeasers( ) {

        var lastTeaserUniqueId = $visibleTeasers.last().data( 'unique-id' );

        if ( !$galleryArea.length || !sourceUrl || !lastTeaserUniqueId ) {
            return true;
        }

        $.get( sourceUrl + lastTeaserUniqueId, function( data ) {
            var selector = 'article[data-type="teaser"]',
                $data = $( data ),
                $teasers = $data.find( selector );

            if ( $galleryArea.offset().top < document.documentElement.scrollTop ) {
                $galleryArea.velocity( 'scroll', slidingDuration );
            }

            //if ( nextPageSource ) {
            //    $shuffleButton.data( 'sourceurl', nextPageSource );
            //} else {
            //    $shuffleButton.velocity( { opacity: 0 }, { visibility: 'hidden' } );
            //}

            $galleryArea.find( selector ).velocity( 'transition.slideLeftBigOut', {
                    duration: slidingDuration,
                    stagger: 50,
                    complete: function( elements ) {
                        $( elements ).parent().replaceWith( $teasers.parent() );
                        images.scale( $teasers );
                        $teasers.velocity( 'transition.slideRightBigIn', {
                            display: '', // remove the property altogether and return to previous display value from CSS
                            duration: slidingDuration,
                            stagger: 50
                        });
                    }
                });
        }).fail(function( ) {
            fallbackUrl = $this.attr( 'href' );
            if ( fallbackUrl ) {
                window.location.href = fallbackUrl;
            }
        });
    }

    /**
    * paginateTeasers.js: remove the visible teasers and show these which were
    * invisible until now.
    * @function slideGalleryTeasers
    */
    function slideGalleryTeasers( ) {

        // We just throw away the vivible items. The remaining are used to fill
        // the space. Due to the CSS rules, the correct number of teasers for
        // the current breakpoint simply slides in (unnecessary ones stay hidden).
        // Actually, `$visibleTeasers.remove();` would do the trick.
        // But to have a beautiful animation (which is also used when loading
        // new items) we use velocity.

        $visibleTeasers.velocity( 'transition.slideLeftBigOut', {
                duration: slidingDuration,
                stagger: 50,
                complete: function( elements ) {
                    $visibleTeasers.remove();
                    $hiddenTeasers.velocity( 'transition.slideRightBigIn', {
                        display: '', // remove the property altogether and return to previous display value from CSS
                        duration: slidingDuration,
                        stagger: 50
                    });
                }
            });
    }

    /**
    * paginateTeasers.js: this function decides, if there are enough hidden
    * teasers to simply switch them. Or if new ones need to be loaded.
    *
    * @function changeGalleryTeasers
    */
    function paginateGalleryTeasers( event ) {

        event.preventDefault();
        $this = $( this );
        $this.blur();
        $galleryArea = $this.closest( '.cp-area' );
        sourceUrl = $this.data( 'sourceurl' );

        $allTeasers = $galleryArea.find( 'article' );
        $visibleTeasers = $allTeasers.filter( ':visible' );
        $hiddenTeasers =  $allTeasers.filter( ':hidden' );

        if ( $hiddenTeasers.length >= $visibleTeasers.length ) {
            slideGalleryTeasers( );
        } else {
            loadGalleryTeasers( );
        }
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
     * @class paginateTeasers
     * @memberOf jQuery.fn
     * @return {object} jQuery-Object for chaining
     */
    $.fn.paginateTeasers = function() {
        return this.on( 'click', paginateGalleryTeasers );
    };
});

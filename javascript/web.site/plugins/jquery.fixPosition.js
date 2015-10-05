/**
 * @fileOverview jQuery plugin to give a fixed position to elements,
 *      depending on the scroll position on the page
 * @author thomas.puppe@zeit.de
 * @version  0.1
 */

/* CHANGELOG
 *
 * 2015-10-02: first draft, every option is hardcoded for a specific case (article-lineage)
 * 2015-10-05: pixelperfection, optimize performance
 */

(function( $ ) {
    function FixPosition( element ) {

        this.node = element;
        this.element = $( element );

        this.currentPositioning = 'absolute';

        this.unchangedCalculationCounter = 0;
        this.lastCalculationTime = 0;

        // on what scrolling positions should the element be positioned fix
        this.minFixedPos = 500;
        this.maxFixedPos = 2000;

        this.init();

        // TODO: return this?
    }

    FixPosition.prototype = {

        init: function() {

            // only use this on Desktop.
            // OPTIMIZE: move this to site.js, so we dont have to check on every instance?
            if ( window.ZMO.breakpoint.get() !== 'desktop' ) {
                return false;
            }

            this.calculateArticlePositions();

            // OPTIMIZE: do we have the $window already available? Is it cached by jQuery?
            // OPTIMIZE: namespace for event handler ?
            var that = this;
            $( window ).on( 'scroll', function() {
                that.scrollThrottling();
            } );

        },

        /*
            This calculates the position of the article begin/end. This is used
            to detect where fixed positioning is used. Because the beginning/end
            will change in the beginning of the page life (image loading, ads),
            we calculate repeatedly, but not too often. When the numbers
            remained unchanged for multiple calls, the recalculation will be no
            longer done. */
        calculateArticlePositions: function() {

            // If the calculation was done too often and nothing changed, stop it!
            if ( this.unchangedCalculationCounter > 5 ) {
                console.log( 'calculation stopped (because of too often).' );
                return;
            }

            var currentDate = new Date(),
                currentTimestamp = currentDate.getTime(),
                winHeight,
                $articleBody,
                articleBodyOffset,
                articleBodyHeight,
                currentMinFixedPos,
                currentMaxFixedPos;

            // If the calculation was done too recently, stop it!
            if ( this.lastCalculationTime > 0 && ( currentTimestamp - this.lastCalculationTime ) < 500 ) {
                console.log( 'calculation stopped (because of too recently).' );
                return;
            }

            // TODO: cache this calculation if the values were stable for several seconds
            // TODO: throttle this calculation

            // TODO: optimize and fail-safe
            // TODO: cache winHeight, recalculate only on window.resize!
            winHeight = $( window ).height();
            // TODO: cache it!
            $articleBody = $( '.article-body' ).eq( 0 );
            articleBodyOffset = $articleBody.offset();
            articleBodyHeight = $articleBody.height();

            currentMinFixedPos = parseInt( articleBodyOffset.top - ( winHeight / 2 ), 10 );
            currentMaxFixedPos = parseInt( articleBodyOffset.top + articleBodyHeight - ( winHeight / 2 ), 10 );

            // for performance: track if nothing has changed
            if ( this.minFixedPos === currentMinFixedPos && this.maxFixedPos === currentMaxFixedPos ) {
                this.unchangedCalculationCounter += 1;
            }

            this.minFixedPos = currentMinFixedPos;
            this.maxFixedPos = currentMaxFixedPos;

            this.lastCalculationTime = currentTimestamp;

            console.log( 'calculation done.' );
        },

        scrollHandler: function() {

            this.calculateArticlePositions();
            // TODO: available in every browser?
            this.currentPosition = window.scrollY;

            // TODO only update the DOM if the status changes. save the current status internally.
            if ( this.currentPosition > this.minFixedPos && this.currentPosition < this.maxFixedPos ) {
                // OPTIMIZE: not hardcoded! Read the base-class on init
                this.element.addClass( 'article-lineage--fixed' );
            } else {
                // OPTIMIZE: not hardcoded! Read the base-class on init
                this.element.removeClass( 'article-lineage--fixed' );
            }

            console.log( 'scrolled.' );
        },

        // OPTIMIZE: this could be reused globally
        scrollThrottling: function() {
            // TODO: Throttling!
            //    - https://developer.mozilla.org/en-US/docs/Web/Events/scroll
            //    - good old window.timeout version
            this.scrollHandler();
        }
    };

    $.fn.fixPosition = function() {
        return this.each( function() {
            new FixPosition( this );
        });
    };

})( jQuery );

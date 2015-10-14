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

        this.scrollThrottlingBlocked = false;

        this.unchangedCalculationCounter = 0;
        this.lastCalculationTime = 0;

        // OPTIMIZE: not hardcoded! Read the base-class on init
        this.baseClass = 'article-lineage';
        this.absolute = false;
        this.fixed = false;

        // on what scrolling positions should the element be positioned fix
        this.minFixedPos = 500;
        this.maxFixedPos = 2000;

        this.$articleBody = undefined;

        // In 2015, we need multiple lines of code to detect the scrolling position
        // (https://developer.mozilla.org/de/docs/Web/API/Window/scrollY)
        this.supportPageOffset = window.pageXOffset !== undefined;
        this.isCSS1Compat = ( ( document.compatMode || '' ) === 'CSS1Compat' );

        this.init();
    }

    FixPosition.prototype = {

        init: function() {

            var that = this;

            // only use this on Desktop.
            // OPTIMIZE: move this to site.js, so we dont have to check on every instance?
            if ( window.ZMO.breakpoint.get() !== 'desktop' ) {
                return false;
            }

            // calculate/select the things that will remain unchanged
            this.$articleBody = $( '.article-body' ).eq( 0 );

            // no article found? stop everything.
            if ( !this.$articleBody.length ) {
                return;
            }

            // OPTIMIZE: do we have the $window already available? Is it cached by jQuery?
            // OPTIMIZE: namespace for event handler ?

            // debounce does not work. That's why I use my own throttling.
            // $( window ).on( 'scroll', $.debounce( that.handleScrolling, 100 ) );

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
                return;
            }

            var currentDate = new Date(),
                currentTimestamp = currentDate.getTime(),
                winHeight,
                articleBodyOffset,
                articleBodyHeight,
                currentMinFixedPos,
                currentMaxFixedPos;

            // If the calculation was done too recently, stop it!
            if ( this.lastCalculationTime > 0 && ( currentTimestamp - this.lastCalculationTime ) < 500 ) {
                return;
            }

            // OPTIMIZE: cache winHeight, recalculate only on window.resize!
            winHeight = $( window ).height();

            articleBodyOffset = this.$articleBody.offset();
            articleBodyHeight = this.$articleBody.height();

            currentMinFixedPos = parseInt( articleBodyOffset.top - ( winHeight / 2 ), 10 );
            currentMaxFixedPos = parseInt( articleBodyOffset.top + articleBodyHeight - ( winHeight / 2 ), 10 );

            // for performance: track if nothing has changed
            if ( this.minFixedPos === currentMinFixedPos && this.maxFixedPos === currentMaxFixedPos ) {
                this.unchangedCalculationCounter += 1;
            }

            this.minFixedPos = currentMinFixedPos;
            this.maxFixedPos = currentMaxFixedPos;

            this.lastCalculationTime = currentTimestamp;

        },

        handleScrolling: function() {

            this.calculateArticlePositions();
            // In 2015, we need multiple lines of code to detect the scrolling position
            // (https://developer.mozilla.org/de/docs/Web/API/Window/scrollY)
            this.currentPosition = this.supportPageOffset ?
                window.pageYOffset : this.isCSS1Compat ?
                    document.documentElement.scrollTop : document.body.scrollTop;

            this.absolute = this.currentPosition > this.maxFixedPos;
            this.fixed = this.currentPosition >= this.minFixedPos && !this.absolute;

            // luckily, jQuery is only changing the DOM if needed
            this.element
                .toggleClass( this.baseClass + '--fixed', this.fixed )
                .toggleClass( this.baseClass + '--absolute', this.absolute );
        },

        /*  This is Throttling! The Scroll Event is thrown very often.
            But there is no need to do all our calculations on every call.
            That's why the event handler is only called every 100ms.

            OPTIMIZE: this could be reused globally.
            OPTIMIZE: After IE9 we can use requestAnimationFrame
                (https://developer.mozilla.org/en-US/docs/Web/Events/scroll)
        */
        scrollThrottling: function() {

            var that = this,
                throttlingTime = 100;

            // The handler is still blocked. So we do not call the actual event handler.
            if ( this.scrollThrottlingBlocked === true ) {
                return;
            }

            // Not blocked. Set a timeout to block for 100ms, and call the actual event handler
            this.scrollThrottlingBlocked = true;
            window.setTimeout( function() {
                that.scrollThrottlingBlocked = false;
            }, throttlingTime );

            this.handleScrolling();

        }
    };

    $.fn.fixPosition = function() {
        return this.each( function() {
            new FixPosition( this );
        });
    };

})( jQuery );

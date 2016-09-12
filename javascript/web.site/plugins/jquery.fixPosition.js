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

(function( $, Zeit ) {
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
        this.bypass = [];
        this.fullwidthElements = [
            '.hide-lineage',
            '.infobox',
            '.inline-gallery',
            '.x-fullwidth',
            '.zg-grafik--default-margin',
            '.zon-grafik',
            '.zon-grafik--map',
            'picture',
            '.infographic',
            '.volume-teaser'
        ];
        this.threshold = 40;
        this.initialMarginLeft = parseInt( this.element.css( 'margin-left' ) );

        // In 2015, we need multiple lines of code to detect the scrolling position
        // (https://developer.mozilla.org/de/docs/Web/API/Window/scrollY,
        // https://developer.mozilla.org/de/docs/Web/API/Window/scrollX)
        this.supportPageOffset = window.pageXOffset !== undefined;
        this.isCSS1Compat = ( ( document.compatMode || '' ) === 'CSS1Compat' );
        this.scrollElement = ( document.documentElement || document.body.parentNode || document.body );

        this.init();
    }

    FixPosition.prototype = {

        init: function() {

            var that = this;

            // only use this on Desktop.
            // OPTIMIZE: move this to site.js, so we dont have to check on every instance?
            if ( Zeit.breakpoint.get() !== 'desktop' ) {
                return false;
            }

            // we do not want to show the elements on iPad, where the "desktop" breakpoint
            // has been enforced via `Zeit.viewport.set( 'banner' );` (in library.html)
            if ( Zeit.viewport.meta && Zeit.viewport.meta.getAttribute( 'content' ) === 'width=1280' ) {
                return false;
            }

            // calculate/select the things that will remain unchanged
            this.$articleBody = $( '.article-body' ).eq( 0 );

            // no article found? stop everything.
            if ( !this.$articleBody.length ) {
                return;
            }

            // special case: liveblogs
            if ( this.$articleBody.find( '.liveblog' ).length ) {
                this.element.addClass( this.baseClass + '--absolute' );
                return;
            }

            // calculate/select more things that will remain unchanged
            this.bypass = this.$articleBody.find( this.fullwidthElements.join() );

            $( window ).on( 'scroll', $.throttle( function() { that.handleScrolling(); }, 100 ) );
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
                nextOffset,
                currentMinFixedPos,
                currentMaxFixedPos;

            // If the calculation was done too recently, stop it!
            if ( this.lastCalculationTime > 0 && ( currentTimestamp - this.lastCalculationTime ) < 500 ) {
                return;
            }

            // OPTIMIZE: cache winHeight, recalculate only on window.resize!
            winHeight = $( window ).height();

            articleBodyOffset = this.$articleBody.offset();
            nextOffset = this.element.next().offset();

            currentMinFixedPos = parseInt( articleBodyOffset.top - ( winHeight / 2 ), 10 );
            currentMaxFixedPos = parseInt( nextOffset.top - ( winHeight / 2 ), 10 );

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
                .removeClass( this.baseClass + '--hidden' ) // needed for variant (A)
                // .css({ top: '' }) // needed for variant (B)
                .toggleClass( this.baseClass + '--fixed', this.fixed )
                .toggleClass( this.baseClass + '--absolute', this.absolute );

            // Handle horizontal scrolling and offset the element so that
            // it visually sticks to the article
            if ( this.fixed ) {
                // calculate and apply offset
                var scrollX = this.supportPageOffset ?
                    window.pageXOffset : this.scrollElement.scrollLeft,
                    offset = this.initialMarginLeft - scrollX;
                this.element.css( 'margin-left', offset + 'px' );
            } else {
                // the only possibility to reset a value that has been set using jQuery's .css()
                // method with IE <= 8 compatibility is to set it to the initial value
                this.element.css( 'margin-left', this.initialMarginLeft + 'px' );
            }

            // check for collisions
            if ( this.fixed && this.bypass.length ) {
                var anchor = ( this.node.firstElementChild || this.element.children().get( 0 ) ).getBoundingClientRect(),
                    // needed for variant (B)
                    // height = anchor.height || 80,
                    i, area;

                for ( i = this.bypass.length - 1; i >= 0; i-- ) {
                    area = this.bypass.get( i ).getBoundingClientRect();

                    if ( anchor.bottom > area.top - this.threshold && anchor.top < area.bottom + this.threshold ) {
                        // variant (A): fade out while overlapping with fullwidth element
                        this.element
                            .addClass( this.baseClass + '--hidden' )
                            .removeClass( this.baseClass + '--fixed' );

                        // variant (B): sticky above fullwidth element
                        // this.element
                        //     .removeClass( this.baseClass + '--fixed' )
                        //     .addClass( this.baseClass + '--absolute' )
                        //     .css({ top: Math.round( this.bypass.get( i ).offsetTop - height - this.threshold ) + 'px' });

                        // collision found: stop searching
                        break;
                    }
                }

            }
        }
    };

    $.fn.fixPosition = function() {
        return this.each( function() {
            new FixPosition( this );
        });
    };

})( jQuery, window.Zeit );

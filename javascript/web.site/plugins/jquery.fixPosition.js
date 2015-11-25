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
        this.bypass = [];
        this.fullwidthElements = [
            '.hide-lineage',
            '.infobox',
            '.inline-gallery__wrap',
            '.liveblog',
            '.x-fullwidth',
            '.zg-grafik--default-margin',
            '.zon-grafik',
            '.zon-grafik--map',
            'picture'
        ];
        this.threshold = 40;

        // In 2015, we need multiple lines of code to detect the scrolling position
        // (https://developer.mozilla.org/de/docs/Web/API/Window/scrollY)
        this.supportPageOffset = window.pageXOffset !== undefined;
        this.isCSS1Compat = ( ( document.compatMode || '' ) === 'CSS1Compat' );

        this.init();
    }

    FixPosition.prototype = {

        init: function() {

            var that = this,
                viewportMetaElement;

            // only use this on Desktop.
            // OPTIMIZE: move this to site.js, so we dont have to check on every instance?
            if ( window.ZMO.breakpoint.get() !== 'desktop' ) {
                return false;
            }

            // we do not want to show the elements on iPad, where the "desktop" breakpoint
            // has been enforced via `window.ZMO.viewport.set( 'banner' );` (library.html, line 115)
            viewportMetaElement = document.getElementById( 'viewport-meta' );
            if ( viewportMetaElement && viewportMetaElement.getAttribute( 'content' ) === 'width=1280' ) {
                return false;
            }

            // calculate/select the things that will remain unchanged
            this.$articleBody = $( '.article-body' ).eq( 0 );
            this.bypass = this.$articleBody.find( this.fullwidthElements.join() );

            // no article found? stop everything.
            if ( !this.$articleBody.length ) {
                return;
            }

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

})( jQuery );

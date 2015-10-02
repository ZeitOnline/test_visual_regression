/**
 * @fileOverview jQuery plugin to give a fixed position to elements,
 *      depending on the scroll position on the page
 * @author thomas.puppe@zeit.de
 * @version  0.1
 */

/* CHANGELOG
 *
 * 2015-10-02: first draft, every option is hardcoded for a specific case (article-lineage)
 */

(function( $ ) {
    function FixPosition( element ) {

        this.node = element;
        this.element = $( element );

        this.currentPositioning = 'absolute';

        // on what scrolling positions should the element be positioned fix
        this.minFixedPos = 500;
        this.maxFixedPos = 2000;

        this.init();
    }

    FixPosition.prototype = {

        init: function() {

            // TODO: optimize and fail-safe
            var winHeight = $( window ).height(),
                $articleBody = $( '.article-body' ).eq( 0 ),
                articleBodyOffset = $articleBody.offset(),
                articleBodyHeight = $articleBody.height();

            this.minFixedPos = parseInt( articleBodyOffset.top - ( winHeight / 2 ), 10 );
            this.maxFixedPos = parseInt( articleBodyOffset.top + articleBodyHeight - ( winHeight / 2 ), 10 );

            // only use this on Desktop.
            // OPTIMIZE: move this to site.js, so we dont have to check on every instance?
            if ( window.ZMO.breakpoint.get() !== 'desktop' ) {
                return false;
            }

            // OPTIMIZE: do we have the $window already available? Is it cached by jQuery?
            // OPTIMIZE: namespace for event handler ?
            var that = this;
            $( window ).on( 'scroll', function() {
                that.scrollThrottling();
            } );

        },

        scrollHandler: function() {

            // available in every browser?
            var currentPosition = window.scrollY;

            window.debugnode = this.node;

            // TODO only update the DOM if the status changes. save the current status internally.
            // TODO: do this via modifier
            if ( currentPosition > this.minFixedPos && currentPosition < this.maxFixedPos ) {
                // OPTIMIZE: not hardcoded! Read the base-class on init
                this.element.addClass( 'article-lineage--fixed' );
            } else {
                // OPTIMIZE: not hardcoded! Read the base-class on init
                this.element.removeClass( 'article-lineage--fixed' );
            }

            console.log( 'scrolled. Pos is ' + this.node.style.position );
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

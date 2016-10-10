/**
 * @fileOverview jQuery Plugin for truncating areas
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
(function( $ ) {

    var maxTeasers = 3;

    /**
     * Initializes instance variables.
     *
     * @constructor
     */
    function Region( node ) {
        this.node = node;
        this.element = $( node );
        this.teasers = this.element.children( 'article' );

        this.init();
    }

    /**
     * Truncate teaser list and add accessible control link
     */
    Region.prototype.init = function() {
        var hidden = this.teasers.length - maxTeasers,
            container, link;

        if ( hidden > 0 ) {
            link = this.element.find( '[aria-controls]' );
            link.children().first().text( '+' + hidden );
            link.on( 'click', function() {
                link.velocity( 'slideUp', { duration: 100 } );
            });

            container = $( '#' + link.attr( 'aria-controls' ) );
            container.append( this.teasers.slice( maxTeasers ) );

            this.element
                .addClass( 'cp-area--truncated' )
                .toggleRegions();
        }
    };

    /**
     * Create an Region instance for each element it is called on.
     */
    $.fn.truncateRegions = function() {
        return this.each( function() {
            new Region( this );
        });
    };

})( jQuery );

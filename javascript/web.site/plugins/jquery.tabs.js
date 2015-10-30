/**
 * @fileOverview tabs jQuery plugin
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
(function( $ ) {
    var defaults = {
            tab: '.studiumbox__headline',
            link: '.studiumbox__headline a',
            page: '.studiumbox__content'
        };

    $.fn.tabs = function( settings ) {
        var options = $.extend( {}, defaults, settings );

        return this.each( function() {
            var box = $( this ),
                tabs = box.find( options.tab ),
                pages = box.find( options.page ),
                clone = pages.first().clone(),
                activeTabClassName = options.tab.slice( 1 ) + '--active',
                activePageClassName = options.page.slice( 1 ) + '--active';

            clone
                .removeClass( activePageClassName )
                .addClass( options.page.slice( 1 ) + '--clone' )
                .insertBefore( pages.first() );

            box.on( 'click', options.link, function( event ) {
                var handle = $( this ).closest( options.tab ),
                    index = tabs.index( handle );

                event.preventDefault();

                if ( !handle.hasClass( activeTabClassName ) ) {
                    tabs.removeClass( activeTabClassName );
                    tabs.eq( index ).addClass( activeTabClassName );
                    pages.removeClass( activePageClassName );
                    pages.eq( index ).addClass( activePageClassName );

                    clone.html( pages.eq( index ).html() );
                }
            });
        });
    };

})( jQuery );

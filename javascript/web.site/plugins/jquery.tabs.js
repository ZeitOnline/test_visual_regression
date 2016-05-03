/**
 * @fileOverview tabs jQuery plugin
 * @author moritz.stoltenburg@zeit.de
 * @version  0.1
 */
(function( $ ) {
    var defaults = {
            tab: '.studiumbox__headline',
            link: '.studiumbox__headline a',
            page: '.studiumbox__content',
            input: '.studiumbox__input',
            preventEmpty: 'studiumbox__headline--prevent_empty',
            mainPage: 'http://ranking.zeit.de/che2016/de/faecher',
            //seperate tracking string for fallback as it varies from form inputs
            tracking: '?wt_zmc=fix.int.zonpmr.zeitde.funktionsbox_studium.che.teaser.button_ohne_fach.x' +
                        '&utm_medium=fix' +
                        '&utm_source=zeitde_zonpmr_int' +
                        '&utm_campaign=funktionsbox_studium' +
                        '&utm_content=che_teaser_button_ohne_fach_x'
        };

    $.fn.tabs = function( settings ) {
        var options = $.extend( {}, defaults, settings );

        // leads to main page if empty form is submitted
        function preventEmptySubmit() {

            var $form = $( options.page + '--clone' ).find( 'form' );

            $form.on( 'submit', function( event ) {
                var $dropdown = $form.find( options.input ),
                    value = $dropdown.find( 'option:selected' ).attr( 'value' );

                if ( !value ) {
                    event.preventDefault();
                    window.location.href = options.mainPage + options.tracking;
                }
            });
        }

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
                    clone.attr( 'id', pages.eq( index ).attr( 'id' ) );

                    if ( handle.hasClass( options.preventEmpty ) ) {
                        preventEmptySubmit();
                    }
                }
            });
        });
    };

})( jQuery );

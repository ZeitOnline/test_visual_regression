/**
 * @fileOverview jQuery Plugin for toggle an area when clicking somewhere else
 * @author anika.szuppa@zeit.de
 * @version  0.1
 */
(function( $, Zeit ) {
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
    * Toggles an area when clicking on another
    * @class toggleOnClick
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.toggleOnClick = function( settings ) {

        // default usecase is the TOC
        var defaults = {
            clickableElementName: 'article-toc__headline',
            toggleElement: '.article-toc__list',
            activeSuffix: '--active',
            formats: [ 'phablet', 'mobile' ],
            show: 'slideUp',
            hide: 'slideDown' },
            options = $.extend( {}, defaults, settings );

        /**
        * bindToggleEvent – toggle show/hide event
        * @param  {object} area HTML-Object the plugin is bound to
        */
        function bindToggleEvent( area ) {

            var $element = $( area ).find( '.' + options.clickableElementName );

            // set click event
            $element.on( 'click', function() {

                var size = Zeit.breakpoint.get();

                // test the size the event should be available at
                if ( $.inArray( size, options.formats ) !== -1 ) {
                    // toggle
                    if ( $( options.toggleElement ).is( ':visible' ) ) {
                        $( options.toggleElement ).velocity( options.show, { duration: 200 } );
                    } else {
                        $( options.toggleElement ).velocity( options.hide, { duration: 200 } );
                    }
                    // toggle suffix if there is one
                    $element.toggleClass( options.clickableElementName + options.activeSuffix );
                }

            });
        }

        return this.each( function() {
            bindToggleEvent( this );
        });
    };
})( jQuery, window.Zeit );

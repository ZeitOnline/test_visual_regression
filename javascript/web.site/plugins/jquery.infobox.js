/**
 * @fileOverview jQuery Plugin for additional functionality in infoboxes
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
(function( $, win ) {
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
    * additional functionality for otherwise css powered infoboxes
    * @class infobox
    * @memberOf jQuery.fn
    * @return {object} jQuery-Object for chaining
    */
    $.fn.infobox = function() {
        var id = $( this ).attr( 'id' ),
            $that = $( this ),
            panels = $that.find( '.infobox-tab__content' ),
            /**
             * responsiveState – check if mobile or desktop version is shown
             * @return {string} 'mobile|desktop'
             */
            responsiveState = function() {
                return $( '#' + id + '--navigation' ).is( ':visible' ) ? 'desktop' : 'mobile';
            },
            /**
             * switchPanel – switch the displayed panel with all aria attribs
             * @param  {object} elem jQuery-Object of the panels tab element
             */
            switchPanel = function( elem ) {
                var panel = $( '#' + $( elem ).attr( 'aria-controls' ) ),
                    showPanels = function( tabs, panels ) {
                        tabs.attr( 'aria-selected', 'true' ).attr( 'aria-expanded', 'true' );
                        tabs.find( 'a' ).addClass( 'infobox-tab__link--active' );
                        panels.attr( 'aria-hidden', 'false' );
                    },
                    hidePanels = function( tabs, panels ) {
                        tabs.attr( 'aria-selected', 'false' ).attr( 'aria-expanded', 'false' );
                        tabs.find( 'a' ).removeClass( 'infobox-tab__link--active' );
                        panels.attr( 'aria-hidden', 'true' );
                    };
                if ( state === 'mobile' ) {
                    if ( elem.attr( 'aria-selected' ) === 'true' ) {
                        hidePanels( elem, panel );
                    } else {
                        // panel is unselected: show it
                        showPanels( elem, panel );
                    }
                } else {
                    // hide all
                    hidePanels( $that.find( '.infobox-tab__title' ), panels );
                    // and show the wanted
                    showPanels( elem, panel );
                }
            },
            /**
             * [changeMenu description]
             * @param  {object} event
             * @param  {string} type  'mobile|desktop'
             * @param  {object} [panel] jQuery-Object of a panels tab element
             */
            changeMenu = function( event, type, panel ) {
                var openPanels = $( '.infobox-tab__title--displayed[aria-selected=true]' ),
                    index;
                if ( type === 'mobile' ) {
                    $( '.infobox__navigation .infobox-tab__title' ).each(function( index ) {
                        $( this )
                            .removeAttr( 'role' )
                            .removeAttr( 'aria-controls' )
                            .removeAttr( 'id' )
                            .removeClass( 'infobox-tab__title--displayed' );
                        if ( $( this ).attr( 'aria-selected' ) === 'true' ) {
                            $( '.infobox-tab .infobox-tab__title' )
                                .eq( index )
                                .attr( 'aria-selected', 'true' )
                                .attr( 'aria-expanded', 'true' )
                                .find( 'a' )
                                .addClass( 'infobox-tab__link--active' );
                        }
                    });
                    $( '.infobox-tab .infobox-tab__title' ).each(function() {
                        $( this )
                            .attr( 'role', $( this ).data( 'role' ) )
                            .attr( 'aria-controls', $( this ).data( 'aria-controls' ) )
                            .attr( 'id', id + $( this ).data( 'index' ) + '-tab' )
                            .addClass( 'infobox-tab__title--displayed' );
                    });
                } else {
                    $( '.infobox-tab .infobox-tab__title' ).each(function() {
                        $( this )
                            .removeAttr( 'role' )
                            .removeAttr( 'aria-controls' )
                            .removeAttr( 'id' )
                            .removeClass( 'infobox-tab__title--displayed' );
                    });
                    $( '.infobox__navigation .infobox-tab__title' ).each(function() {
                        $( this )
                            .attr( 'role', $( this ).data( 'role' ) )
                            .attr( 'aria-controls', $( this ).data( 'aria-controls' ) )
                            .attr( 'id', id + '-' + $( this ).data( 'index' ) + '-tab' )
                            .addClass( 'infobox-tab__title--displayed' );
                    });
                    if ( state === 'desktop' && openPanels.length !== 1 ) {
                        index = openPanels.first().data( 'index' ) || 1;
                        switchPanel( $( '#' + id + '-' + index + '-tab' ) );
                    }
                    if ( panel ) {
                        switchPanel( $( '#' + id + '-' + panel + '-tab' ) );
                    }
                }
            },
            state;

        return this.each( function() {
            // initially set state
            state = responsiveState();
            // mark all as hidden
            panels.attr( 'aria-hidden', true );
            // copy links
            $( '.infobox-tab__title', this ).clone( true ).appendTo( '#' + id + '--navigation' );
            // listener change in a11y functionality
            $( this ).on( 'infoboxChange', changeMenu );
            // trigger for first load
            $that.trigger( 'infoboxChange', [ state, 1 ] );
            // state checker
            $( window ).on( 'resize', function() {
                var newstate = responsiveState();
                if ( newstate !== state ) {
                    state = newstate;
                    $that.trigger( 'infoboxChange', [ newstate ] );
                }
            });
            // actions
            $( '.infobox-tab__title', this ).on( 'click', function( event ) {
                event.preventDefault();
                switchPanel( $( this ) );
            });
            $( '.infobox-tab__title', this ).on( 'keypress', function( event ) {
                var code = event.keyCode || event.which;
                event.preventDefault();
                if ( code === 13 || code === 32 ) { // enter or space
                    $( this ).trigger( 'click' );
                }
            });
        });
    };
})( jQuery, window );

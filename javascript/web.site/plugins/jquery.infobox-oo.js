/**
 * @fileOverview jQuery Plugin for additional functionality in infoboxes
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
(function( $, window ) {

    function InfoboxOO( element ) {
        this.id = element.id;
        this.element = element;
        this.isMobile = this.isMobileView();
        this.panels = $( this ).find( '.infobox-tab__content' );

        this.init();
    }

    InfoboxOO.prototype.init = function() {
        this.panels.each( this.markHidden( this ) );

        // copy links
        $( '.infobox-tab__title', this.element )
            .clone( true )
            .attr( 'tabindex', '-1' )
            .appendTo( '#' + this.id + '--navigation' );

        // listener change in a11y functionality
        $( this ).on( 'infoboxChange', this.changeMenu );

        // trigger for first load
        $( this ).trigger( 'infoboxChange', this.pageHashInBox() );

        $( window ).on( 'resize', this.checkResize() );

        // actions
        $( '.infobox-tab__title', this.element ).on( 'click', function( event ) {
            event.preventDefault();
            $( this ).switchPanel();
            if ( this.isMobile === false ) {
                var id = $( this ).attr( 'id' );
                if ( history.pushState ) {
                    history.pushState( null, null, '#' + id.substring( 0, id.length - 4 ) );
                }
            }
        });

        $( '.infobox-tab__title', this ).on( 'keypress', function( event ) {
            var code = event.keyCode || event.which;
            event.preventDefault();
            if ( code === 13 || code === 32 ) { // enter or space
                $( this ).trigger( 'click' );
            }
        });
    };

    InfoboxOO.prototype.switchPanel = function() {
        var panel = $( '#' + $( this.element ).attr( 'aria-controls' ) );

        if ( this.isMobile ) {
            if ( this.element.attr( 'aria-selected' ) === 'true' ) {
                this.hidePanels( this.element, panel );
            } else {
                this.showPanels( this.element, panel );
            }
        } else {
            // hide all
            this.hidePanels( $( this ).find( '.infobox-tab__title' ), this.panels );
            // and show the wanted
            this.showPanels( this.element, panel );
        }
    };

    InfoboxOO.prototype.markHidden = function( element ) {
        element.attr( 'aria-hidden', 'true' );
    };

    InfoboxOO.prototype.markVisible = function( element ) {
        element.attr( 'aria-hidden', 'false' );
    };

    InfoboxOO.prototype.isMobileView = function() {
        return !$( '#' + this.id + '--navigation' ).is( ':visible' ); // TODO get rid of ugly negation
    };

    InfoboxOO.prototype.showPanels = function( tabs, panels ) {
        tabs.attr( 'aria-selected', 'true' ).attr( 'aria-expanded', 'true' );
        tabs.find( 'a' ).addClass( 'infobox-tab__link--active' );
        this.markVisible( panels );
    };

    InfoboxOO.prototype.hidePanels = function( tabs, panels ) {
        tabs.attr( 'aria-selected', 'false' ).attr( 'aria-expanded', 'false' );
        tabs.find( 'a' ).removeClass( 'infobox-tab__link--active' );
        this.markHidden( panels );
    };

    InfoboxOO.prototype.pageHashInBox = function() {
        var hash, position = 0;

        if ( window.location.hash ) {
            hash = window.location.hash.substring( 1 );
            $( this ).find( '.infobox-tab' ).each( function( index, element ) {
                if ( element.id === hash ) {
                    position = index + 1;
                    return false;
                }
            });
            return position > 0 ? position : 1;
        }
    };

    InfoboxOO.prototype.switchPanel = function() {

    };

    InfoboxOO.prototype.checkResize = function() {
        var newState = this.isMobileView();

        if ( newState !== this.isMobile ) {
            this.isMobile = newState;
            $( this ).trigger( 'infoboxChange' );
        }
    };

    InfoboxOO.prototype.changeMenu = function( event, panel ) {
        var openPanels = $( '.infobox-tab__title--displayed[aria-selected=true]' ),
            index;

        if ( this.isMobile ) {
            $( '.infobox__navigation .infobox-tab__title' ).each(function( index ) {
                $( this )
                    .removeAttr( 'role' )
                    .removeAttr( 'aria-controls' )
                    .removeAttr( 'id' )
                    .removeClass( 'infobox-tab__title--displayed' )
                    .attr( 'tabindex', '-1' );
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
                    .attr( 'id', this.id + '-' + $( this ).data( 'index' ) + '-tab' )
                    .attr( 'tabindex', '0' )
                    .addClass( 'infobox-tab__title--displayed' );
            });
        } else {
            $( '.infobox-tab .infobox-tab__title' ).each(function() {
                $( this )
                    .removeAttr( 'role' )
                    .removeAttr( 'aria-controls' )
                    .removeAttr( 'id' )
                    .removeClass( 'infobox-tab__title--displayed' )
                    .attr( 'tabindex', '-1' );
            });
            $( '.infobox__navigation .infobox-tab__title' ).each(function() {
                $( this )
                    .attr( 'role', $( this ).data( 'role' ) )
                    .attr( 'aria-controls', $( this ).data( 'aria-controls' ) )
                    .attr( 'id', this.id + '-' + $( this ).data( 'index' ) + '-tab' )
                    .attr( 'tabindex', '0' )
                    .addClass( 'infobox-tab__title--displayed' );
            });
            if ( this.isMobile === false && openPanels.length !== 1 ) {
                index = openPanels.first().data( 'index' ) || 1;
                this.switchPanel( $( '#' + this.id + '-' + index + '-tab' ) );
            }
        }
        if ( panel ) {
            this.switchPanel( $( '#' + this.id + '-' + panel + '-tab' ) );
        }
    };

    $.fn.infoboxOO = function() {

        return this.each( function() {
            new InfoboxOO( this );
        });
    };

})( jQuery, window );

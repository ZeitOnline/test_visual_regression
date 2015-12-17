/**
 * @fileOverview jQuery Plugin for additional functionality in infoboxes
 * @author nico.bruenjes@zeit.de
 * @version  0.1
 */
(function( $, window ) {

    function InfoboxOO( infobox ) {
        this.id = infobox.id;
        this.isDesktop = this.isDesktopView();
        this.infobox = $( infobox );
        this.navigation = $( '#' + this.id + '-navigation', this.infobox );
        this.tabpanels = $( '.infobox-tab__panel', this.infobox );
        this.tabtitles = $( '.infobox-tab__title', this.infobox )
                            .clone()
                            .appendTo( this.navigation );
        this.tablinks = $( this.tabtitles ).find( 'a' );
        this.currentTab = this.tablinks.first();

        this.init();
    }

    InfoboxOO.prototype.init = function() {
        var self = this;

        this.navigation.attr( 'role', 'tablist' );

        this.tabtitles
            .attr( 'role', 'tab' )
            .addClass( 'infobox-tab__title--displayed' );

        this.tablinks.each( function() {
            $( this ).attr( 'aria-controls', $( this ).data( 'aria-controls' ) );
        });

        // TODO switch to tab according to location.hash
        this.switchTo( this.tablinks.first() );

        this.tablinks.on( 'click', function( event ) {
            event.preventDefault();
            self.switchTo( $( this ) );
            if ( self.isDesktop ) {
                var id = $( this ).attr( 'id' );
                if ( history.pushState ) {
                    history.pushState( null, null, '#' + id.substring( 0, id.length - 4 ) );
                }
            }
        });

        $( window ).on( 'resize', function() {
            // check if mobile & react if needed
        });

    };

    InfoboxOO.prototype.switchTo = function( selectedTab ) {
        var relatedPanelId = '#' + selectedTab.attr( 'aria-controls' ),
            relatedPanel = $( relatedPanelId );

        this.currentTab.removeClass( 'infobox-tab__link--active' );
        this.currentTab = selectedTab;
        selectedTab.addClass( 'infobox-tab__link--active' );

        this.markHidden( this.tabpanels );
        this.markVisible( relatedPanel );
    };

    InfoboxOO.prototype.markHidden = function( panels ) {
        panels.attr({
            'aria-hidden': true,
            'aria-selected': false
        });
    };

    InfoboxOO.prototype.markVisible = function( panels ) {
        panels.attr({
            'aria-hidden': false,
            'aria-selected': true
        });
    };

    InfoboxOO.prototype.isDesktopView = function() {
        return $( '#' + this.id + '-navigation', this.infobox ).is( ':visible' );
    };

    InfoboxOO.prototype.checkResize = function() {

    };

    InfoboxOO.prototype.getCurrentHash = function() {
        if ( window.location.hash ) {
            var hash = window.location.hash.substring( 1 );
            $( '.infobox-tab', this.infobox ).each( function( index, element ) {
                if ( element.id === hash ) {
                    return element.id;
                }
            });
        }
        return false;
    };

    InfoboxOO.prototype.changeMenu = function( event, panel ) {

    };

    $.fn.infoboxOO = function() {

        return this.each( function() {
            new InfoboxOO( this );
        });
    };

})( jQuery, window );

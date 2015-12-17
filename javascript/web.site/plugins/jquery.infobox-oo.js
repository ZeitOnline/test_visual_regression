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
        this.tabtitlesMobile = $( '.infobox-tab__title', this.infobox );
        this.tabtitles = this.tabtitlesMobile
                            .clone()
                            .appendTo( this.navigation );
        this.tablinks = $( this.tabtitles ).find( 'a' );
        this.tablinksMobile = $( this.tabtitlesMobile ).find( 'a' );
        this.currentTab = this.tablinks.first();

        this.init();
    }

    InfoboxOO.prototype.init = function() {
        var self = this;

        this.navigation.attr( 'role', 'tablist' );

        if ( this.isDesktop ) {
            // TODO refactor this
            this.tabtitles
                .attr( 'role', 'tab' )
                .addClass( 'infobox-tab__title--displayed' );
            this.tablinks.each( function() {
                $( this ).attr( 'aria-controls', $( this ).data( 'aria-controls' ) );
            });
        } else {
            this.tabtitlesMobile
                .attr( 'role', 'tab' )
                .addClass( 'infobox-tab__title--displayed' );
            this.tablinksMobile.each( function() {
                $( this ).attr( 'aria-controls', $( this ).data( 'aria-controls' ) );
            });
            this.markHidden( this.tabpanels );
        }

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

        this.tablinksMobile.on( 'click', function( event ) {
            event.preventDefault();
            self.switchTo( $( this ) );
        });

        $( window ).on( 'resize', function() {
            if ( self.isDesktopView() === false ) {
                self.tabtitlesMobile
                    .attr( 'role', 'tab' )
                    .addClass( 'infobox-tab__title--displayed' );
                self.tabtitles
                    .removeClass( 'infobox-tab__title--displayed' );
            }
        });

    };

    InfoboxOO.prototype.switchTo = function( selectedTab ) {
        var relatedPanelId = '#' + selectedTab.attr( 'aria-controls' ),
            relatedPanel = $( relatedPanelId );

        if ( this.isDesktop ) {
            this.currentTab.removeClass( 'infobox-tab__link--active' );
            this.currentTab = selectedTab;
            selectedTab.addClass( 'infobox-tab__link--active' );

            this.markHidden( this.tabpanels );
            this.markVisible( relatedPanel );
        } else {
            selectedTab.toggleClass( 'infobox-tab__link--active' );
            if ( selectedTab.hasClass( 'infobox-tab__link--active' )) {
                this.markVisible( relatedPanel );
            } else {
                this.markHidden( relatedPanel );
            }
        }

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

    $.fn.infoboxOO = function() {

        return this.each( function() {
            new InfoboxOO( this );
        });
    };

})( jQuery, window );

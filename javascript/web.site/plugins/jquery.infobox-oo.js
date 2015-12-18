/**
 * @fileOverview jQuery Plugin for additional functionality in infoboxes
 * @author nico.bruenjes@zeit.de, valentin.vonguttenberg@zeit.de
 * @version  0.2
 */
(function( $, window ) {

    function InfoboxOO( infobox ) {
        this.id = infobox.id;
        this.infobox = $( infobox );
        this.navigation = $( '#' + this.id + '-navigation', this.infobox );
        this.tabpanels = $( '.infobox-tab__panel', this.infobox );
        this.tabtitles = $( '.infobox-tab__title', this.infobox )
                            .clone()
                            .appendTo( this.navigation );
        this.tabs = $( this.tabtitles ).find( 'a' );
        this.hasSidebar = this.hasSidebarNavigation();

        this.init();
    }

    InfoboxOO.prototype.init = function() {
        var self = this,
            openTab = this.getSelectedTabByHash() || this.tabs.first();

        this.navigation.attr( 'role', 'tablist' );
        this.setTabsAndTabtitles();

        if ( this.hasSidebar ) {
            this.switchTo( openTab );
        } else {
            this.markHidden( this.tabpanels );
        }

        this.infobox.on( 'click', '.infobox-tab__link', function( event ) {
            var tab = $( this );
            event.preventDefault();
            self.switchTo( tab );
            if ( self.hasSidebarNavigation() ) {
                var id = tab.attr( 'id' );
                if ( history.pushState ) {
                    history.pushState( null, null, '#' + id.substring( 0, id.length - 4 ) );
                }
            }
        });

        $( window ).on( 'resize', function() {
            var openTabs = self.infobox.find( 'infobox-tab__link--active' ).first();
            self.switchNavigationMode( openTab );
        });
    };

    InfoboxOO.prototype.hasSidebarNavigation = function() {
        return this.navigation.is( ':visible' );
    };

    InfoboxOO.prototype.switchTo = function( selectedTab ) {
        var relatedPanelId = '#' + selectedTab.attr( 'aria-controls' ),
            relatedPanel = $( relatedPanelId );

        if ( this.hasSidebar ) {
            this.tabs.removeClass( 'infobox-tab__link--active' );
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

    /**
    * Switches the presentation of navigation according to the hasSidebar boolean
    *
    * @param {boolean} hasSidebar Wether to use sidebar navigation or if false the
    *                  folded navigation.
    * @param {jQuery} openTab Defines the panel that is opened after the switch
    */
    InfoboxOO.prototype.switchNavigationMode = function( openTab ) {
        // Do not rebuild the navigation if not necessary
        if ( this.hasSidebar === this.hasSidebarNavigation()) {
            return;
        }

        this.hasSidebar = this.hasSidebarNavigation();
        this.setTabsAndTabtitles();

        if ( this.hasSidebar ) {
            this.switchTo( openTab );
        } else {
            this.markHidden( this.tabpanels.not( openTab ) );
        }
    };

    /**
    * Adds the necessary attributes to the tab navigation according to the
    * navigation mode (sidebar or folded).
    */
    InfoboxOO.prototype.setTabsAndTabtitles = function() {

        this.tabtitles
            .removeAttr( 'role', 'tab' )
            .removeClass( 'infobox-tab__title--displayed' );
        this.tabs.removeAttr( 'aria-controls' );

        if ( this.hasSidebar ) {
            this.tabtitles = $( '.infobox__navigation .infobox-tab__title', this.infobox );
        } else {
            this.tabtitles = $( '.infobox-tab .infobox-tab__title', this.infobox );
        }

        this.tabtitles
            .attr( 'role', 'tab' )
            .addClass( 'infobox-tab__title--displayed' );

        this.tabs = this.tabtitles.find( 'a' );
        this.tabs.each( function() {
            $( this ).attr( 'aria-controls', $( this ).data( 'aria-controls' ) );
        });
    };

    /**
    * Checks the URL for possible hashs that are related to tabs of this infobox.
    *
    * @return {jQuery} The tab related to the hash or undefined if no related
    *                  tab has been found.
    */
    InfoboxOO.prototype.getSelectedTabByHash = function() {
        if ( window.location.hash ) {
            var hash = window.location.hash.substring( 1 );
            return this.tabs.filter( '#' + hash + '-tab' );
        }
    };

    $.fn.infoboxOO = function() {
        return this.each( function() {
            new InfoboxOO( this );
        });
    };

})( jQuery, window );

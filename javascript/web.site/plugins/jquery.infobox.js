/**
 * @fileOverview jQuery Plugin for additional functionality in infoboxes
 * @author nico.bruenjes@zeit.de, valentin.vonguttenberg@zeit.de
 * @version  0.2
 */
(function( $, window, location ) {

    /**
    * Clones the tab (navigation) links in their own div for creating
    * a sidebar navigation and initializes instance variables.
    *
    * @constructor
    */
    function Infobox( infobox ) {
        this.infobox = $( infobox );
        this.navigation = this.infobox.find( '#' + this.infobox.attr( 'id' ) + '-navigation' );
        this.hasSidebar = this.hasSidebarNavigation();
        this.tabpanels = this.infobox.find( '.infobox-tab__panel' );
        this.tabtitles = this.infobox.find( '.infobox-tab__title' )
                            .clone()
                            .appendTo( this.navigation );
        this.tabs = this.tabtitles.find( 'a' );
        this.curOpenTab = undefined;

        this.init();
    }

    /**
    * Sets up variables, expands the first tab if hasSidebar is true
    * and creates event listeners.
    */
    Infobox.prototype.init = function() {
        var self = this, // needed in event listeners
            selectedTab = this.getSelectedTabByHash() || this.tabs.first();

        this.curOpenTab = selectedTab;
        this.infobox.find( '.infobox-tab__title a' ).removeAttr( 'id' );
        this.navigation.attr( 'role', 'tablist' );
        this.setNavigationMode();

        if ( this.hasSidebar ) {
            this.switchTo( selectedTab );
        } else {
            this.setVisibility( this.tabpanels, false );
        }

        // Switch to selected tab and update location.hash and curOpenTab
        this.infobox.on( 'click', '.infobox-tab__link', function( event ) {
            var tab = $( this );
            event.preventDefault();
            self.curOpenTab = tab;
            self.switchTo( tab );
            if ( self.hasSidebar ) {
                var tabId = tab.attr( 'id' );
                if ( history.pushState ) {
                    history.pushState( null, null, '#' + tabId.substring( 0, tabId.length - 4 ) );
                }
            }
        });

        // Check if layout change is necessary when resizing
        $( window ).on( 'resize', function() {
            if ( self.hasSidebar !== self.hasSidebarNavigation() ) {
                self.hasSidebar = self.hasSidebarNavigation();
                self.setNavigationMode();
                self.switchTo( $( '#' + self.curOpenTab.attr( 'id' ) ) );
            }
        });
    };

    /**
    * @return {boolean} true if in the sidebar should be visible according
    *                   to CSS, false otherwise
    */
    Infobox.prototype.hasSidebarNavigation = function() {
        return this.navigation.is( ':visible' );
    };

    /**
    * Select the given tab in the infobox and make its panel visible. When
    * in sidebar mode (according to hasSidebar boolean), only one active
    * panel is allowed so all panels – except the panel to the given tab –
    * are hidden. If there is no sidebar, multiple panels may be expanded
    * at the same time and the function works like a toggle and shows
    * or hides the panel to the given tab
    *
    * @param {jQuery} selectedTab the tab to be shown or toggled
    */
    Infobox.prototype.switchTo = function( selectedTab ) {
        var relatedPanelId = '#' + selectedTab.attr( 'aria-controls' ),
            relatedPanel = $( relatedPanelId );

        if ( this.hasSidebar ) {
            this.tabs.removeClass( 'infobox-tab__link--active' );
            this.toggleTabActive( this.tabs, false );

            selectedTab.addClass( 'infobox-tab__link--active' );
            this.toggleTabActive( selectedTab, true );

            this.setVisibility( this.tabpanels, false );
            this.setVisibility( relatedPanel, true );
        } else {
            selectedTab.toggleClass( 'infobox-tab__link--active' );
            if ( selectedTab.hasClass( 'infobox-tab__link--active' )) {
                this.toggleTabActive( selectedTab, true );
                this.setVisibility( relatedPanel, true );
            } else {
                this.toggleTabActive( selectedTab, false );
                this.setVisibility( relatedPanel, false );
            }
        }
    };

    /**
    * Sets aria-selected and aria-expanded attributes for tab(s) according
    * to the given boolean.
    *
    * @param {jQuery} tabs The tab(s) to be toggled
    * @param {boolean} isActive If true the tabs are marked selected and
    *                  expanded, if false these attributes are set to false
    */
    Infobox.prototype.toggleTabActive = function( tabs, isActive ) {
        tabs.attr({
            'aria-selected': isActive,
            'aria-expanded': isActive
        });
    };

    /**
    * Sets the aria-hidden and aria-selected attributes of the given
    * jQuery element(s) to hidden & not selected or visible & selected
    * according to the given boolean.
    *
    * @param {jQuery} panels The panel(s) to be set visible or hidden
    * @param {boolean} isVisible Sets the panel(s) visible if true or
    *                  hidden otherwise
    */
    Infobox.prototype.setVisibility = function( panels, isVisible ) {
        panels.attr({
            'aria-hidden': !isVisible,
            'aria-selected': isVisible
        });
    };

    /**
    * When the sidebar is visible, the cloned links in the navigation area
    * are used, otherwise the links above the panels are used. This function
    * sets the necessary attributes and updates instance variables according to
    * the hasSidebar state.
    */
    Infobox.prototype.setNavigationMode = function() {
        this.tabtitles
            .removeAttr( 'role' )
            .removeClass( 'infobox-tab__title--displayed' );

        this.tabs.each( function() {
            $( this )
                .removeAttr( 'id' )
                .removeAttr( 'aria-controls' )
                .removeClass( 'infobox-tab__link--active' );
        });

        this.setVisibility( this.tabpanels, false );

        if ( this.hasSidebar ) {
            this.tabtitles = this.infobox.find( '.infobox__navigation .infobox-tab__title' );
        } else {
            this.tabtitles = this.infobox.find( '.infobox-tab .infobox-tab__title' );
        }

        this.tabtitles
            .attr( 'role', 'tab' )
            .addClass( 'infobox-tab__title--displayed' );

        this.tabs = this.tabtitles.find( 'a' );
        this.tabs.each( function() {
            $( this )
                .attr( 'aria-controls', $( this ).data( 'aria-controls' ) )
                .attr( 'id', $( this ).data( 'id' ) );
        });
    };

    /**
    * Checks the URL for possible hashs that are related to tabs of this infobox.
    *
    * @return {jQuery} The tab related to the hash or undefined if no related
    *                  tab has been found.
    */
    Infobox.prototype.getSelectedTabByHash = function() {
        if ( location.hash ) {
            var hash = location.hash.substring( 1 );
            return this.tabs.filter( '#' + hash + '-tab' );
        }
    };

    /**
    * Create an infobox instance for each element it is called on.
    */
    $.fn.infobox = function() {
        return this.each( function() {
            new Infobox( this );
        });
    };

})( jQuery, window, location );

/**
 * @fileOverview jQuery Plugin for additional functionality in infoboxes
 * @author nico.bruenjes@zeit.de, valentin.vonguttenberg@zeit.de
 * @version  0.2
 */
(function( $, window, location ) {

    /**
     * Initializes instance variables.
     *
     * @constructor
     */
    function Infobox( infobox ) {
        this.infobox = $( infobox );
        this.navigation = this.infobox.find( '.infobox__navigation' );
        this.tabpanels = this.infobox.find( '.infobox-tab__panel' );
        this.tabs = this.infobox.find( '.infobox-tab__link' );
        this.hasSidebar = false;

        this.init();
    }

    /**
     * Clones the tab (navigation) links to create a sidebar navigation
     * for desktop view, expands the first tab if sidebar is visible and
     * creates event listeners.
     */
    Infobox.prototype.init = function() {
        var self = this; // needed in event listeners

        this.tabs.removeAttr( 'id' );
        this.infobox.find( '.infobox-tab__title' )
            .clone()
            .appendTo( this.navigation );
        this.navigation.attr( 'role', 'tablist' );
        this.updateNavigationMode();
        this.showActiveTab();

        // Switch to selected tab and update location.hash
        this.infobox.on( 'click', '.infobox-tab__link', function( event ) {
            event.preventDefault();

            self.selectTab( $( this ) );

            if ( self.hasSidebar ) {
                if ( history.replaceState ) {
                    history.replaceState( null, null, this.hash );
                }
            }
        });

        // Check if layout change is necessary when resizing
        $( window ).on( 'resize', function() {
            if ( self.hasSidebar !== self.hasSidebarNavigation() ) {
                self.updateNavigationMode();
                self.showActiveTab();
            }
        });
    };

    /**
     * Show active tab
     */
    Infobox.prototype.showActiveTab = function() {
        var hashTab = this.getSelectedTabByHash();

        if ( this.hasSidebar ) {
            this.selectTab( hashTab || this.tabs.first() );
        } else if ( hashTab ) {
            this.selectTab( hashTab );
        }
    };

    /**
     * @return {boolean} true if the sidebar is visible, false otherwise
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
     * @param {jQuery} tab the tab to be shown or toggled
     */
    Infobox.prototype.selectTab = function( tab ) {
        var relatedPanel = $( '#' + tab.attr( 'aria-controls' ) );

        if ( this.hasSidebar ) {
            this.setTabsActive( this.tabs, false );
            this.setTabsActive( tab, true );

            this.setPanelsVisible( this.tabpanels, false );
            this.setPanelsVisible( relatedPanel, true );
        } else {
            var isTabActive = ( tab.attr( 'aria-expanded' ) === 'true' );

            this.setTabsActive( tab, !isTabActive );
            this.setPanelsVisible( relatedPanel, !isTabActive );
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
    Infobox.prototype.setTabsActive = function( tabs, isActive ) {
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
    Infobox.prototype.setPanelsVisible = function( panels, isVisible ) {
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
    Infobox.prototype.updateNavigationMode = function() {
        this.hasSidebar = this.hasSidebarNavigation();
        this.tabs.removeAttr( 'id' );

        this.setTabsActive( this.tabs, false );
        this.setPanelsVisible( this.tabpanels, false );

        if ( this.hasSidebar ) {
            this.tabs = this.infobox.find( '.infobox__navigation .infobox-tab__link' );
        } else {
            this.tabs = this.infobox.find( '.infobox__content .infobox-tab__link' );
        }

        this.tabs.attr( 'id', function() {
            return this.getAttribute( 'data-id' );
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
            var hashTab = this.tabs.filter( location.hash + '-tab' );

            if ( hashTab.length ) {
                return hashTab;
            }
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

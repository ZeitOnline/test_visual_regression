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
        this.accordion = this.infobox.find( '.infobox__content' );
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
        this.updateNavigationMode();
        this.showActiveTab();

        // Switch to selected tab and update location.hash
        this.infobox.on( 'click', '.infobox-tab__link', function( event ) {
            event.preventDefault();

            self.selectTab( $( this ) );

            if ( self.hasSidebar ) {
                if ( history.pushState ) {
                    history.pushState( null, null, this.hash );
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

        // When going back in the browser history update the open tab
        // according to the location.hash
        $( window ).on( 'hashchange', function( event ) {
            if ( self.hasSidebar ) {
                var tab = ( location.hash ) ? self.getSelectedTabByHash() : self.tabs.first();

                if ( tab ) {
                    event.preventDefault();
                    self.selectTab( tab );
                }
            }
        });

        // Configure keyboard navigation
        this.infobox.on( 'keydown', function( event ) {
            // do nothing if there are other special keys involved
            if ( event.altKey || event.shiftKey || event.ctrlKey || event.metaKey ) {
                return;
            }

            var index = self.tabs.index( document.activeElement ),
                keyCode,
                focus,
                select;

            if ( index !== -1 ) {
                keyCode = event.keyCode || event.which;

                switch ( keyCode ) {
                    case 13: // return
                    case 32: // space
                        select = index;
                        break;

                    case 35: // end
                        select = self.tabs.length - 1;
                        break;

                    case 36: // home
                        select = 0;
                        break;

                    case 37: // left
                    case 38: // up
                        focus = --index;
                        break;

                    case 39: // right
                    case 40: // down
                        focus = ++index % self.tabs.length;
                        break;
                }
            }

            if ( focus !== undefined ) {
                event.preventDefault();
                self.tabs.eq( focus ).focus();
            } else if ( select !== undefined ) {
                event.preventDefault();
                self.selectTab( self.tabs.eq( select ).focus() );
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
            this.setTabsActive( this.tabs, false, -1 );
            this.setTabsActive( tab, true, 0 );

            this.setPanelsVisible( this.tabpanels, false );
            this.setPanelsVisible( relatedPanel, true );
        } else {
            var isTabActive = ( tab.attr( 'aria-expanded' ) === 'true' );

            this.setTabsActive( tab, !isTabActive );
            this.setPanelsVisible( relatedPanel, !isTabActive );
        }
    };

    /**
     * Sets aria-selected and aria-expanded attributes to the given boolean.
     *
     * @param {jQuery}  tabs        Set of matched elements to be toggled
     * @param {boolean} isActive
     * @param {numeric} tabindex    tabindex value {-1|0} [optional]
     */
    Infobox.prototype.setTabsActive = function( tabs, isActive, tabindex ) {
        tabs.attr({
            'aria-selected': isActive,
            'aria-expanded': isActive,
            'tabindex': tabindex || 0
        });
    };

    /**
     * Sets the aria-hidden attribute to the given boolean.
     *
     * @param {jQuery} panels Set of matched elements to set visible or hidden
     * @param {boolean} isVisible
     */
    Infobox.prototype.setPanelsVisible = function( panels, isVisible ) {
        panels.attr({
            'aria-hidden': !isVisible
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
            this.tabs = this.navigation.find( '.infobox-tab__link' );
            // Mark-up navigation being a tabbed interface component
            this.navigation.attr( 'role', 'tablist' );
            // Remove accordion component mark-up
            this.accordion
                .removeAttr( 'role' )
                .removeAttr( 'aria-multiselectable' );
        } else {
            this.tabs = this.accordion.find( '.infobox-tab__link' );
            // Remove tabbed interface component mark-up
            this.navigation.removeAttr( 'role' );
            // Mark-up content being an accordion component
            this.accordion.attr({
                'role': 'tablist',
                'aria-multiselectable': true
            });
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
            var hashTab = this.tabs.filter( location.hash );

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

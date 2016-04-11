/**
 * @fileOverview Module for navigation actions
 * @version  0.1
 */
/**
 * main_nav.js: module for main navigation
 * @module main_nav
 */
define(['jquery'], function() {

    var $main_nav_trigger = $('#js-main-nav-trigger');
    var $main_nav_content = $('#js-main-nav-content');
    var $main_nav = $('#js-main-nav');
    var $open_menu;
    var $open_menu_container;
    var mobile_menu_open = false;
    var has_mobile_nav; // will be filled in initMobileNav/initDesktopNav

    /**
     * main-nav.js: initialize navigation for small screens
     * @function initMobileNav
     */
    var initMobileNav = function() {
        has_mobile_nav = true;

        // enable hamburger
        $main_nav_trigger.off('click.nav-handler');
        $main_nav_trigger.on('click.nav-handler', function(e) {
            e.preventDefault();
            e.stopPropagation();
            $main_nav_content.toggleClass('is-open');
            mobile_menu_open = !mobile_menu_open;
        });
    };

    /**
     * main-nav.js: initialize navigation for bigger screens
     * @function initDesktopNav
     */
    var initDesktopNav = function() {
        has_mobile_nav = false;
    };

    /**
     * main-nav.js: close open menu
     * @function closeOpenMenu
     * @param  {object} e event object
     */
    var closeOpenMenu = function(e) {
        if (has_mobile_nav) {
            if (mobile_menu_open && ! $(e.target).closest('.is-open').length) {
                // close mobile nav when open
                $main_nav_content.removeClass('is-open');
                mobile_menu_open = false;
            }
        } else {
            if ($open_menu && ! $(e.target).closest('.is-open').length) {
                // close desktop nav dropdowns when open
                $open_menu.removeClass('is-open');
                $open_menu = undefined;
                $open_menu_container.removeClass('has-open-menu');
                $open_menu_container = undefined;
            }
        }
    };

    /**
     * main-nav.js: toggle section dropdown menu
     * @function toggleSectionMenu
     * @param  {object} e event object
     */
    var toggleSectionMenu = function(e) {
        e.preventDefault();
        e.stopPropagation();

        var $link = $(this),
            $menu = $link.next(),
            $item = $link.parent();

        if ($open_menu) {
            $open_menu.removeClass('is-open');
            $open_menu_container.removeClass('has-open-menu');
        }

        if (!$open_menu || !$open_menu.is($menu)) {
            $open_menu = $menu.addClass('is-open');
            $open_menu_container = $item.addClass('has-open-menu');
        } else {
            $open_menu = undefined;
            $open_menu_container = undefined;
        }
    };

    /**
     * main-nav.js: initialize navigation
     * @function init
     */
    var init = function() {
        // disable hover fallback
        $main_nav.removeClass('has-hover');

        // enable drop downs
        $main_nav.on('click', '.js-main-nav-section-trigger', toggleSectionMenu);

        // init nav depending on screen size
        if ($main_nav_trigger.is(':visible')) {
            initMobileNav();
        } else {
            initDesktopNav();
        }

        // close all menus whenever user clicks anywhere else
        $(document.body).on('click', closeOpenMenu);

        // deliver the right navigation type on window resize
        $(window).resize(function() {
            if ( !has_mobile_nav && $main_nav_trigger.is(':visible') ) {
                initMobileNav();
            } else if ( has_mobile_nav && $main_nav_trigger.is(':hidden') ) {
                initDesktopNav();
            }
        });
    };

    return {
        init: init
    };

});

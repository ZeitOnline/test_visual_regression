/* global console, define, alert */
define(['jquery'], function() {

  var $main_nav_trigger = $('#js-main-nav-trigger');
  var $main_nav_content = $('#js-main-nav-content');
  var $main_nav_sections = $('.main-nav__section');
  var $main_nav_section_triggers = $('.js-main-nav-section-trigger');
  var $main_nav_section_contents = $('.js-main-nav-section-content');
  var $main_nav = $('#js-main-nav');
  var $ressort_slider_container;
  var $ressort_slider_strip;
  var $open_menu;
  var $open_menu_container;
  var mobile_menu_open = false;
  var full_nav_breakpoint = 768;
  var has_mobile_nav; // will be filled in init_mobile_nav/init_desktop_nav

  /**
   * [init_mobile_nav description]
   * @return {[type]}
   */
  var init_mobile_nav = function() {
    has_mobile_nav = true;

    // enable hamburger
    $main_nav_trigger.off('click.nav-handler');
    $main_nav_trigger.on('click.nav-handler', function(e) {
      e.preventDefault();
      e.stopPropagation();
      $main_nav_content.toggleClass('is-open');
      mobile_menu_open = !mobile_menu_open;
    });

    // enable accordeons
    $main_nav_section_triggers.off('click.nav-handler');
    $main_nav_section_triggers.on('click.nav-handler', function(e) {
      e.preventDefault();
      e.stopPropagation();
      var $current_content = $(this).next();
      $main_nav_section_contents.not($current_content).removeClass('is-open');
      $(this).next().toggleClass('is-open');
    });
  };

  /**
   * [init_desktop_ressort_slider description]
   * @return {[type]}
   */
  var init_desktop_ressort_slider = function() {
    $ressort_slider_container = $('#js-main-nav-ressorts-slider-container');
    $ressort_slider_strip = $('#js-main-nav-ressorts-slider-strip');
    var hidden_offset = $ressort_slider_strip.outerWidth() - $ressort_slider_container.width();
    if (hidden_offset > 0) {
      $main_nav.addClass('has-topic-slider');
      var $left_arrow = $ressort_slider_container.find('.main-nav__ressorts__slider-arrow--left');
      var $right_arrow = $ressort_slider_container.find('.main-nav__ressorts__slider-arrow--right');
      var move_by = hidden_offset + $left_arrow.width()*3;
      $left_arrow.off();
      $left_arrow.click(function() {
        $ressort_slider_strip.css('left', 0);
        $right_arrow.removeClass('is-inactive');
        $left_arrow.addClass('is-inactive');
      });
      $right_arrow.off();
      $right_arrow.click(function() {
        $ressort_slider_strip.css('left', -1 * move_by);
        $left_arrow.removeClass('is-inactive');
        $right_arrow.addClass('is-inactive');
      });
    }
  };

  /**
   * [init_desktop_nav description]
   * @return {[type]}
   */
  var init_desktop_nav = function() {
    has_mobile_nav = false;

    // disable hover fallback
    $main_nav.removeClass('has-hover');

    // enable drop downs
    $main_nav_section_triggers.off('click.nav-handler');
    $main_nav_section_triggers.on('click.nav-handler', function(e) {
      e.preventDefault();
      e.stopPropagation();

      // close all other menus
      $main_nav_section_contents.not($(this).next()).removeClass('is-open');
      $main_nav_section_triggers.not($(this)).removeClass('is-open');
      $main_nav_sections.not($(this).parent()).removeClass('has-open-menu');

      // open correct one
      $open_menu = $(this).toggleClass('is-active').next().toggleClass('is-open');
      $open_menu_container = $(this).parent().toggleClass('has-open-menu');
    });

    // init topics/ressort slider if necessary
    init_desktop_ressort_slider();
  };

  /**
   * [close_open_menu description]
   * @return {[type]}
   */
  var close_open_menu = function() {
    if (window.innerWidth < full_nav_breakpoint) {
      if (mobile_menu_open) {
        // close mobile nav when open
        $main_nav_content.removeClass('is-open');
        mobile_menu_open = !mobile_menu_open;
      }
    } else {
      if ($open_menu_container && $open_menu) {
        // close desktop nav dropdowns when open
        $open_menu.removeClass('is-open');
        $open_menu = undefined;
        $open_menu_container.removeClass('has-open-menu');
        $open_menu_container = undefined;
      }
    }
  };

  /**
   * [init description]
   * @return {[type]}
   */
  var init = function() {
    // init nav depending on screen size
    if (window.innerWidth < full_nav_breakpoint) {
      init_mobile_nav();
    } else {
      init_desktop_nav();
    }

    // close all menus whenever user clicks anywhere else
    $('body').click(function(e) {
      close_open_menu();
    });

    // deliver the right navigation type on window resize
    $(window).resize(function() {
        if ( !has_mobile_nav && (window.innerWidth < full_nav_breakpoint) ) {
            init_mobile_nav();
        } else if ( has_mobile_nav && (window.innerWidth >= full_nav_breakpoint) ) {
            init_desktop_nav();
        }
    });
  };

  return {
    init: init
  };

});

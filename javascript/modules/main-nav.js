/* global console, define, alert */

define(['jquery'], function() {

  var $main_nav_trigger = $('#js-main-nav-trigger');
  var $main_nav_content = $('#js-main-nav-content');
  var $main_nav_section_triggers = $('.main-nav__section__trigger');
  var $main_nav_section_contents = $('.main-nav__section__content:not(.is-always-open)');
  var $main_nav = $('#js-main-nav');

  var init_mobile_nav = function() {
    $main_nav_trigger.click(function(e) {
      e.preventDefault();
      $main_nav_content.toggle();
    });

    $main_nav_section_triggers.click(function(e) {
      e.preventDefault();
      var $current_content = $(this).next();
      $main_nav_section_contents.not($current_content).hide();
      $(this).next().toggle();
    });
  };

  var init_desktop_nav = function() {
    $main_nav.removeClass('has-hover');
    $main_nav_section_triggers.click(function(e) {
      e.preventDefault();
      $(this).toggleClass('is-active').next().toggleClass('is-open');
      $(this).parent().toggleClass('has-open-menu');
    });
  };

  var init = function() {
    if (window.innerWidth < 768) {
      init_mobile_nav();
    } else {
      init_desktop_nav();
    }
  };

  return {
    init: init
  };

});
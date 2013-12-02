/* global console, define, alert */

define(['jquery'], function() {

  var $main_nav_trigger = $('#js-main-nav-trigger');
  var $main_nav_content = $('#js-main-nav-content');
  var $main_nav_section_triggers = $('.main-nav__section__trigger');
  var $main_nav_section_contents = $('.main-nav__section__content:not(.is-always-open)');
  var $main_nav = $('#js-main-nav');
  var $ressort_slider_container;
  var $ressort_slider_strip;

  var init_mobile_nav = function() {
    $main_nav_trigger.click(function(e) {
      e.preventDefault();
      $main_nav_content.toggle();
    });

    $main_nav_section_triggers.click(function(e) {
      e.preventDefault();
      var $current_content = $(this).next();
      $main_nav_section_contents.not($current_content).removeClass('is-open');
      $(this).next().toggleClass('is-open');
    });
  };

  var init_desktop_ressort_slider = function() {
    $ressort_slider_container = $('#js-main-nav-ressorts-slider-container');
    $ressort_slider_strip = $('#js-main-nav-ressorts-slider-strip');
    var hidden_offset = $ressort_slider_strip.outerWidth() - $ressort_slider_container.width();
    if (hidden_offset > 0) {
      $main_nav.addClass('has-topic-slider');
      var $left_arrow = $ressort_slider_container.find('.main-nav__ressorts__slider-arrow--left');
      var $right_arrow = $ressort_slider_container.find('.main-nav__ressorts__slider-arrow--right');
      var move_by = hidden_offset + $left_arrow.width()*2;
      $left_arrow.click(function() {
        $ressort_slider_strip.css('left', 0);
        $right_arrow.removeClass('is-inactive');
        $left_arrow.addClass('is-inactive');
      });
      $right_arrow.click(function() {
        $ressort_slider_strip.css('left', -1 * move_by);
        $left_arrow.removeClass('is-inactive');
        $right_arrow.addClass('is-inactive');
      });
    }
  };

  var init_desktop_nav = function() {
    $main_nav.removeClass('has-hover');
    $main_nav_section_triggers.click(function(e) {
      e.preventDefault();
      $(this).toggleClass('is-active').next().toggleClass('is-open');
      $(this).parent().toggleClass('has-open-menu');
    });
    init_desktop_ressort_slider();
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
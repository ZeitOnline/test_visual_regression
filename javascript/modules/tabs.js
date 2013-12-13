/* global console, define, alert */

define(['jquery'], function() {

  var init = function() {
    var $tabs = $('.tabs');
    $tabs.each(function(idx, container) {
      var $triggers = $(container).find('.tabs__head__tab');
      var $contents = $(container).find('.tabs__content');

      // hide all but first content pane
      $contents.slice(1).hide();

      // bind triggers
      $triggers.each(function(idx, trigger) {
        $(trigger).click(function(e) {
          e.preventDefault();
          $triggers.removeClass('is-active');
          $(this).addClass('is-active');
          $contents.hide();
          $contents.eq(idx).show();
        });
      });
    });
  };

  return {
    init: init
  };

});
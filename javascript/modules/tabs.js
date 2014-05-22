/* global console, define, alert */

define(['jquery'], function() {

  /**
   * [init description]
   * @return {[type]}
   */
  var init = function() {
    var $tabs = $('.tabs');
    $tabs.each(function(idx, container) {
      var $triggers = $(container).find('.tabs__head__tab');
      var $contents = $(container).find('.tabs__content');

      // bind triggers
      $triggers.each(function(idx, trigger) {
        $(trigger).click(function(e) {
          e.preventDefault();
          $triggers.removeClass('is-active');
          $(this).addClass('is-active');
          $contents.removeClass('is-active');
          $contents.eq(idx).addClass('is-active');
        });
      });
    });
  };

  return {
    init: init
  };

});

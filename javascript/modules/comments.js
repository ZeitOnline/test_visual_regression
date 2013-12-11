/* global console, define, alert */

define(['jquery'], function() {
  var init = function() {
    var $comments_trigger = $('#js-comments-trigger');
    var $comments = $('#js-comments');
    var $article = $('#js-article');

    $comments_trigger.click(function() {
      if ($comments_trigger.css('position') === 'absolute') {
        var comments_width = $(window).innerWidth() - $article.outerWidth();
        if (comments_width > 700) {
          comments_width = 700;
        }
        $comments.css('width', comments_width);
      } else {
        $comments.css('width', '100%');
      }
      $article.toggleClass('show-comments');
    });
  };

  return {
    init: init
  };

});
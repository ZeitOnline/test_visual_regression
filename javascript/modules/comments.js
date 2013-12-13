/* global console, define, alert */

define(['jquery'], function() {
  var init = function() {
    var $comments_trigger = $('#js-comments-trigger');
    var $comments = $('#js-comments');
    var $article = $('#js-article');
    var $comments_head = $('#js-comments-head');
    var $comments_tabs_head = $('#js-comments-tabs-head');
    var $comments_body = $('#js-comments-body');
    var $comments_all_list = $('#js-comments-all-list');
    var $comments_next = $('#js-comments-body-next');
    var $comments_prev = $('#js-comments-body-prev');
    var comments_body_height = 0;

    $comments_next.click(function() {
      var current_top_offset = parseInt($comments_all_list.css('top').replace('px',''), 10);
      $comments_all_list.css('top', current_top_offset + comments_body_height);
      $('html, body').animate({
        scrollTop: $comments_trigger.offset().top
      }, 250);
    });

    $comments_prev.click(function() {
      var current_top_offset = parseInt($comments_all_list.css('top').replace('px',''), 10);
      $comments_all_list.css('top', current_top_offset - comments_body_height);
      $('html, body').animate({
        scrollTop: $comments_trigger.offset().top
      }, 250);
    });

    $comments_trigger.click(function() {
      var window_width = $(window).innerWidth();

      // restrict width of comments box when outside
      if (window_width >= 1280) {
        var comments_width = window_width - $article.outerWidth();
        if (comments_width > 700) {
          comments_width = 700;
        }
        $comments.css('width', comments_width);
      } else {
        $comments.css('width', '100%');
      }

      // show the comments
      $article.toggleClass('show-comments');

      // handle tablet/desktop size with paginated comments
      if (window_width >= 768) {
        comments_body_height = $comments.innerHeight() - document.getElementById('js-comments-body').offsetTop;
        $comments_body.css('height', comments_body_height);
        if ($comments_body.height() < $comments_all_list.height()) {
          $comments_body.addClass('is-longer');
        }
      } else {
        $comments_body.css('height', 'auto');
      }
    });
  };

  return {
    init: init
  };

});
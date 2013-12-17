/* global console, define, alert */

define(['jquery', 'modules/tabs'], function() {
  var $comments_trigger = $('#js-comments-trigger');
  var $comments = $('#js-comments');
  var $page_wrap_inner = $('#js-page-wrap-inner');
  var $comments_tabs_head = $('#js-comments-tabs-head');
  var $comments_body = $('#js-comments-body');
  var $comments_all_list;
  var $comments_older = $('#js-comments-body-older');
  var $comments_newer = $('#js-comments-body-newer');
  var comments_body_height = 0;
  var window_width = 0;

  var recalculate_pagination = function() {
    // handle tablet/desktop size with paginated comments
    if (window_width >= 768) {
      // calculate maximum height for comments and set
      $comments_all_list = $('#js-comments-body .tabs__content.is-active .comments__list');
      comments_body_height = $comments.outerHeight() - document.getElementById('js-comments-body').offsetTop;
      $comments_body.css('height', comments_body_height);
      // detect whether we even need pagination
      if ($comments_body.height() < $comments_all_list.height()) {
        $comments_body.addClass('show-older-trigger');
      }
    // handle mobile widths
    } else {
      $comments_body.css('height', 'auto');
    }
  };

  var init = function() {
    // bind pagination for older comments
    $comments_older.click(function() {
      // calculate new comments offset
      var current_top_offset = parseInt($comments_all_list.css('top').replace('px',''), 10);
      var list_offset = current_top_offset - comments_body_height;
      $comments_body.addClass('show-newer-trigger');
      // detect whether we need the older trigger for another round
      if (Math.abs(list_offset) + comments_body_height > $comments_all_list.height()) {
        $comments_body.removeClass('show-older-trigger');
      }
      $comments_all_list.css('top', list_offset);
      // scroll to top of comments
      $('html, body').animate({
        scrollTop: $comments_trigger.offset().top
      }, 250);
    });

    // bind pagination for newer comments
    $comments_newer.click(function() {
      // calculate new comments offset
      var current_top_offset = parseInt($comments_all_list.css('top').replace('px',''), 10);
      var list_offset = current_top_offset + comments_body_height;
      $comments_body.addClass('show-older-trigger');
      // detect whether we need the newer trigger for another round
      if (list_offset >= 0) {
        $comments_body.removeClass('show-newer-trigger');
      }
      $comments_all_list.css('top', list_offset);
      // scroll to top of comments
      $('html, body').animate({
        scrollTop: $comments_trigger.offset().top
      }, 250);
    });

    // handle tab switch: recalculate comment metrics for new comment list
    $comments_tabs_head.find('.tabs__head__tab').click(function(e) {
      $comments_body.removeClass('has-older-comments has-newer-comments');
      recalculate_pagination();
    });

    // bind comments trigger to toggle comments
    $comments_trigger.click(function() {
      window_width = $(window).innerWidth();

      if (window_width >= 1280) {
        // on big screens find out how much outside space there is
        var comments_width = window_width - $page_wrap_inner.outerWidth();
        // restrict width of comments
        if (comments_width > 700) {
          comments_width = 700;
        }
        $comments.css('width', comments_width);
      } else {
        // mobile case: show full width comments
        $comments.css('width', '100%');
      }

      // finally show the comments
      $page_wrap_inner.toggleClass('show-comments');

      // calculate if we need pagination
      recalculate_pagination();
    });
  };

  return {
    init: init
  };

});
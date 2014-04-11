/* global console, define, alert, _ */
define(['jquery', 'underscore', 'modules/tabs'], function() {

    var $comments_trigger = $('#js-comments-trigger');
    var $comments = $('#js-comments');
    var $page_wrap_inner = $('#js-page-wrap-inner');
    var $comments_tabs_head = $('#js-comments-tabs-head');
    var $comments_body = $('#js-comments-body');
    var $comments_active_list;
    var $comments_older = $('#js-comments-body-older');
    var $comments_newer = $('#js-comments-body-newer');
    var comments_body_height = null;
    var window_width = null;

    /**
     * handles comment pagination
     */
    var calculatePagination = function() {

        // handle tablet/desktop size with paginated comments
        if (window_width >= 768) {

            // calculate maximum height for comments and set
            $comments_active_list = $('#js-comments-body .tabs__content.is-active .comments__list');
            comments_body_height = $comments.outerHeight() - document.getElementById('js-comments-body').offsetTop;
            $comments_body.css('height', comments_body_height);

            // detect whether we even need pagination
            if (comments_body_height < $comments_active_list.height()) {
                $comments_body.addClass('show-older-trigger');
            }

            var current_top_offset = parseInt($comments_active_list.css('top').replace('px',''), 10);

            if (current_top_offset < 0) {
                $comments_body.addClass('show-newer-trigger');
            }

        // handle mobile widths
        } else {
            $comments_body.css('height', '');
        }
    };

    /**
     * Reply to comment
     */
    var replyToComment = function() {
        var cid  = this.getAttribute('data-cid'),
            name = this.getAttribute('data-name'),
            form = document.forms['js-comments-form'],
            node = $(form).find('.comments__recipient').first(),
            html = 'Antwort auf: <a href="#cid-' + cid + '">' + name + '</a>';

        form.elements.pid.value = cid;
        node.html(html).find("a[href^='#']").animateScroll();
    };

    /**
     * Report comment
     */
    var reportComment = function() {
        var cid  = this.getAttribute('data-cid'),
            comment = $('#cid-' + cid),
            form = comment.next('.comment__report__form'),
            template, templateData;

        if ( ! form.length ) {
            template = _.template(
                $('#js-report-comment-template').html()
            );

            templateData = {
                commentId: cid
            };

            form = $(template(templateData)).insertAfter(comment);
        }

        form.slideToggle();
    };

    /**
     * Cancel report
     */
    var cancelReport = function(e) {
        e.preventDefault();

        $(this).closest('.comment__report__form').slideUp();
    };

    /**
     * Toggle comments
     */
    var toggleComments = function() {
        $page_wrap_inner.toggleClass('show-comments');

        // this should not be done on every toggle, but we have to do it once *after* comments get visible. refactor
        calculatePagination();
    };

    /**
     * Get window inner width
     */
    var getWindowWidth = function() {
        return document.documentElement.clientWidth || document.body.clientWidth || $(document).width();
    };

    /**
     * Initialize layout
     */
    var initLayout = function() {
        window_width = getWindowWidth();

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
            $comments.css('width', '');
        }

        // calculate if we need pagination
        calculatePagination();
    };

    /**
     * Update layout, debounced
     */
    var updateLayout = _.debounce(function(e) {

        initLayout();

    }, 250); // Maximum run of once per 250 milliseconds

    /**
     * Initialize comment section
     */
    var init = function() {

        initLayout();

        // register event handlers
        $comments_body.on('click', '.js-reply-to-comment', replyToComment);
        $comments_body.on('click', '.js-report-comment', reportComment);
        $comments_body.on('click', '.js-cancel-report', cancelReport);
        $comments_trigger.click(toggleComments);
        $(window).on('resize', updateLayout);
        // enable animation of dynamically added anchor links
        $comments_body.on('click', ".js-cancel-report a[href^='#']", function(e){ $(this).animateScroll(); });

        // mimic hover for the sake of grunticons - change later (SVG Sprites FTW)
        $('.icon-flag').hover(function() {
            $(this).removeClass('icon-flag').addClass('icon-flag-hover');
        }, function() {
            $(this).removeClass('icon-flag-hover').addClass('icon-flag');
        });
        $('.icon-reply').hover(function() {
            $(this).removeClass('icon-reply').addClass('icon-reply-hover');
        }, function() {
            $(this).removeClass('icon-reply-hover').addClass('icon-reply');
        });

        // on document ready: check for url hash to enable anchor links and return urls
        $(function() {
            var anchor = window.location.hash.slice(1);

            if (/^cid-\d/.test(anchor)) {
                toggleComments();

                var target = document.getElementById(anchor) || document.getElementsByName(anchor)[0];

                if (!target) {
                    return;
                }

                $('html, body').animate({
                    scrollTop: $(target).offset().top
                }, 500);
            }
        });

        // bind pagination for older comments
        $comments_older.click(function() {

            // calculate new comments offset
            var current_top_offset = parseInt($comments_active_list.css('top').replace('px',''), 10);
            var list_offset = current_top_offset - comments_body_height;
            $comments_body.addClass('show-newer-trigger');

            // detect whether we need the older trigger for another round
            if (Math.abs(list_offset) + comments_body_height > $comments_active_list.height()) {
                $comments_body.removeClass('show-older-trigger');
            }
            $comments_active_list.css('top', list_offset);

            // scroll to top of comments
            $('html, body').animate({
                scrollTop: $comments_trigger.offset().top
            }, 250);
        });

        // bind pagination for newer comments
        $comments_newer.click(function() {

            // calculate new comments offset
            var current_top_offset = parseInt($comments_active_list.css('top').replace('px',''), 10);
            var list_offset = current_top_offset + comments_body_height;
            $comments_body.addClass('show-older-trigger');

            // detect whether we need the newer trigger for another round
            if (list_offset >= 0) {
                $comments_body.removeClass('show-newer-trigger');
            }
            $comments_active_list.css('top', list_offset);

            // scroll to top of comments
            $('html, body').animate({
                scrollTop: $comments_trigger.offset().top
            }, 250);
        });


        // handle tab switch: recalculate comment metrics for new comment list
        $comments_tabs_head.find('.tabs__head__tab').click(function(e) {
            $comments_body.removeClass('show-newer-trigger show-older-trigger');
            calculatePagination();
        });

    };

    return {
        init: init
    };

});

/* global console, define, alert, _ */
define(['jquery', 'underscore', 'modules/tabs'], function() {

    var $comments_trigger = $('#js-comments-trigger'),
        $comments = $('#js-comments'),
        $page_wrap_inner = $('#js-page-wrap-inner'),
        $comments_tabs_head = $('#js-comments-tabs-head'),
        $comments_body = $('#js-comments-body'),
        $comments_active_list,
        $comments_older = $('#js-comments-body-older'),
        $comments_newer = $('#js-comments-body-newer'),
        comments_body_height = null,
        window_width = null,
        inputEvent = ('oninput' in document.createElement('input')) ? 'input' : 'keypress';

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
            comment = $(this).closest('article'),
            form = comment.find('.js-reply-form');

        if ( ! form.length ) {
            form = $('#js-comments-form')
                .clone()
                .removeAttr('id')
                .addClass('js-reply-form')
                .css('display', 'none')
                .appendTo(comment);
            form.find('input[type="submit"]').prop('disabled', true);
            form.find('input[name="pid"]').val(cid);
        }

        if (form.is(':hidden')) {
            hideOtherForms();
        }

        form.slideToggle().find('textarea').focus(); // generic = :input:enabled:visible:first
    };

    var hideOtherForms = function() {
        $comments_body.find('form').filter(':visible').slideToggle();
    };

    /**
     * Report comment
     */
    var reportComment = function() {
        var cid  = this.getAttribute('data-cid'),
            comment = $(this).closest('article'),
            form = comment.find('.js-report-form'),
            template, templateData;

        if ( ! form.length ) {
            template = _.template(
                $('#js-report-comment-template').html()
            );

            templateData = {
                commentId: cid
            };

            form = $(template(templateData)).addClass('js-report-form').appendTo(comment);
        }

        if (form.is(':hidden')) {
            hideOtherForms();
        }

        form.slideToggle().find('textarea').focus();
    };

    /**
     * Cancel report
     */
    var cancelReport = function(e) {
        e.preventDefault();

        $(this).closest('.js-report-form').slideUp();
    };

    /**
     * Submit report
     */
    var submitReport = function(e) {
        e.preventDefault();

        var sendurl = "http://community.zeit.de/services/json",
            input = this.form.elements;

        // var generateJSONPNumber = function () {};

        $.ajax({
            url: sendurl,
            data: {
                method:     'flag.flagnote',
                flag_name:  'kommentar_bedenklich',
                uid:        input.uid.value,
                content_id: input.content_id.value,
                note:       input.note.value
            },
            // jsonpCallback: 'jsonp' + generateJSONPNumber(),
            dataType: 'jsonp',
            success: function(data) {
                if (data) {
                    if (!data['#error']) {
                        alert("Danke! Ihre Meldung wird an die Redaktion weitergeleitet.");
                    }
                    else {
                    }
                }
            }
         });

    };

    /**
     * Enable form submit button
     */
    var enableForm = function() {
        var blank = /^\s*$/.test(this.value);

        $(this.form).find('.button').prop('disabled', blank);
    };

    /**
     * Toggle comments
     */
    var toggleComments = function() {
        $(document.body).toggleClass('show-comments');
        // this should not be done on every toggle, but we have to do it once *after* comments get visible. refactor
        // we should not have to do it at all but document.getElementById('js-comments-body').offsetTop there makes it necessary
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
     * Toggle sharing box
     */
    var toggleSharing = function() {
        $(this).find('.article__sharing__icon').toggleClass('icon-sharebox-share').toggleClass('icon-sharebox-close');
        $('.article__sharing__services').toggleClass('blind');
    };

    /**
     * Initialize comment section
     */
    var init = function() {

        if (! $comments.length) {
            return;
        }

        initLayout();

        $('.js-toggle-sharing').on('click', toggleSharing);

        // register event handlers
        $comments_body.on('click', '.js-reply-to-comment', replyToComment);
        $comments_body.on('click', '.js-report-comment', reportComment);
        $comments_body.on('click', '.js-cancel-report', cancelReport);
        $comments_body.on('click', '.js-submit-report', submitReport);
        $comments.on(inputEvent, '.js-required', enableForm);
        $comments_trigger.click(toggleComments);
        $(window).on('resize', updateLayout);

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

/* global console, define, alert, _ */
define(['jquery', 'underscore', 'modules/tabs'], function() {

    var $socialServices = $('#js-social-services'),
        $comments = $('#js-comments'),
        $page = $('#js-page-wrap-inner'),
        $commentsTabsHead = $('#js-comments-tabs-head'),
        $commentsBody = $('#js-comments-body'),
        $commentsActiveList = $('#js-comments-body .tabs__content.is-active .comments__list'),
        $buttonUp = $('#js-comments-button-up'),
        $buttonDown = $('#js-comments-button-down'),
        documentWidth = null,
        inputEvent = ('oninput' in document.createElement('input')) ? 'input' : 'keypress';

    /**
     * handles comment pagination
     */
    var calculatePagination = function() {
        // handle tablet/desktop size with paginated comments
        if (documentWidth >= 768) {
            var commentsScrollHeight = getHiddenProperty($comments, 'scrollHeight');

            // detect whether we even need pagination
            if ($comments.height() < commentsScrollHeight) {
                $comments.addClass('show-older-trigger');
            }

            var currentOffset = parseInt($commentsActiveList.css('top'), 10);

            if (currentOffset < 0) {
                $comments.addClass('show-newer-trigger');
            }
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

        var sendurl = this.form.getAttribute('action'),
            form = this.form,
            input = this.form.elements;

        // $(this).prop('disabled', true).html('Senden');

        $.ajax({
            url: sendurl,
            data: {
                method:     'flag.flagnote',
                flag_name:  'kommentar_bedenklich',
                uid:        input.uid.value,
                content_id: input.content_id.value,
                note:       input.note.value
            },
            jsonpCallback: 'jsonp' + generateJSONPNumber(),
            dataType: 'jsonp',
            success: function(response) {
                if (response) {
                    if (!response['#error']) {
                        var $form = $(form),
                            html = $('#js-report-success-template').html(),
                            height = $form.css('height'),
                            newHeight;

                        $form.html(html);

                        newHeight = $form.css('height');

                        $form
                            .css('height', height)
                            .animate({height: newHeight});
                    }
                    else {
                        // what else?
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
    };

    /**
     * Initialize layout
     */
    var initLayout = function() {
        documentWidth = getDocumentWidth();

        if (documentWidth >= 1280) {
            // on big screens find out how much outside space there is
            var commentsWidth = documentWidth - $page.outerWidth();
            // restrict width of comments
            if (commentsWidth > 700) {
                commentsWidth = 700;
            }
            $comments.css('width', commentsWidth);
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
     * Scroll comments list
     */
    var scrollComments = function(e) {
        var direction = e.target.getAttribute('data-direction'),
            currentOffset = parseInt($commentsActiveList.css('top'), 10),
            windowTop = $(window).scrollTop(),
            windowBottom = windowTop + document.documentElement.clientHeight,
            visibleTop = getHiddenOffset($buttonUp).top - $buttonUp.height(), // maybe do it once?
            visibleBottom = getHiddenOffset($buttonDown).top, // maybe do it once?
            newOffset,
            commentsOffset,
            visibleArea;

        // calculate maximum height for comments
        if (windowTop > visibleTop) {
            visibleTop = windowTop;
        }
        if (windowBottom < visibleBottom) {
            visibleBottom = windowBottom;
        }

        visibleArea = Math.round(visibleBottom - visibleTop);

        switch (direction) {
            case 'up':
                // calculate new comments offset
                newOffset = currentOffset + visibleArea;
                $comments.addClass('show-older-trigger');

                // detect whether we need the newer trigger for another round
                if (newOffset >= 0) {
                    newOffset = 0; // never scroll over the top
                    $comments.removeClass('show-newer-trigger');
                }

                // ensure maximum viewport
                commentsOffset = Math.floor($commentsBody.offset().top);

                if (windowTop < commentsOffset) {
                    $('html, body').animate({
                        scrollTop: commentsOffset
                    }, 1000);
                }

                break;

            default:
                // calculate new comments offset
                newOffset = currentOffset - visibleArea;
                $comments.addClass('show-newer-trigger');

                // detect whether we need the older trigger for another round
                if (Math.abs(newOffset) + visibleArea > $commentsActiveList.height()) {
                    $comments.removeClass('show-older-trigger');
                }
        }

        $commentsActiveList.css('top', newOffset);
    };

    /**
     * Helper functions
     */
    var getHiddenProperty = function(element, property) {
        element.css('display', 'block');
        var value = element.prop(property);
        element.css('display', '');

        return value;
    };

    var getHiddenOffset = function(element) {
        element.css('display', 'block');
        var offset = element.offset();
        element.css('display', '');

        return offset;
    };

    var hideOtherForms = function() {
        $commentsBody.find('form').filter(':visible').slideToggle();
    };

    var generateJSONPNumber = function() {
        return (1361462065627 + Math.floor(Math.random()*101));
    };

    var getDocumentWidth = function() {
        return document.documentElement.clientWidth || document.body.clientWidth || $(document).width();
    };

    /**
     * Initialize comment section
     */
    var init = function() {

        if (! $comments.length) {
            return;
        }

        initLayout();

        // register event handlers
        $socialServices.on('click', '.js-toggle-sharing', toggleSharing);
        $socialServices.on('click', '.js-comments-trigger', toggleComments);
        $commentsBody.on('click', '.js-reply-to-comment', replyToComment);
        $commentsBody.on('click', '.js-report-comment', reportComment);
        $commentsBody.on('click', '.js-cancel-report', cancelReport);
        $commentsBody.on('click', '.js-submit-report', submitReport);
        $comments.on('click', '.js-scroll-comments', scrollComments);
        $comments.on(inputEvent, '.js-required', enableForm);
        $(window).on('resize', updateLayout);

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

        // handle tab switch: recalculate comment metrics for new comment list
        $commentsTabsHead.on('click', '.tabs__head__tab', function(e) {
            $commentsActiveList = $(e.target.hash);
            $comments.removeClass('show-newer-trigger show-older-trigger');
            calculatePagination();
        });

    };

    return {
        init: init
    };

});

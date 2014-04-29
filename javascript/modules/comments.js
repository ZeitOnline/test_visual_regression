/* global console, define, _ */
define(['jquery', 'underscore', 'modules/tabs'], function() {

    var $socialServices = $('#js-social-services'),
        $comments = $('#js-comments'),
        $page = $('#js-page-wrap-inner'),
        $commentsTabsHead = $('#js-comments-tabs-head'),
        $commentsBody = $('#js-comments-body'),
        $commentsActiveList = $('#js-comments-body .tabs__content.is-active .comments__list'),
        currentOffset = 0,
        slideDuration = 300,
        paginated = false,
        cache = {},
        inputEvent = ('oninput' in document.createElement('input')) ? 'input' : 'keypress';

    /**
     * handles comment pagination
     */
    var calculatePagination = function() {
        var documentWidth = getCachedValue('documentWidth');

        $comments.removeClass('show-newer-trigger show-older-trigger');

        // handle tablet/desktop size with paginated comments
        if (documentWidth >= 768) {
            var commentsScrollHeight = getHiddenProperty($comments, 'scrollHeight');

            // detect whether we even need pagination
            if ($comments.height() < commentsScrollHeight + currentOffset) {
                $comments.addClass('show-older-trigger');
            }

            if (currentOffset < 0) {
                $comments.addClass('show-newer-trigger');
            }

            paginated = true;
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

        showForm(form, comment);
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

        showForm(form, comment);
    };

    /**
     * Show form
     */
    var showForm = function(form, comment) {
        var checkHeight = false;

        if (form.is(':hidden')) {
            hideOtherForms();
            checkHeight = paginated;
        }

        form.slideToggle(slideDuration, function() {
            if (checkHeight) {
                var needed = comment.offset().top + comment.height(),
                    available = getCachedValue('visibleBottom'),
                    missing = needed - available;

                if (missing > 0) {
                    setCurrentOffset(currentOffset - missing);
                    calculatePagination();
                }
            }

            form.find('textarea').focus();
        });
    };

    /**
     * Cancel report
     */
    var cancelReport = function(e) {
        e.preventDefault();

        $(this).closest('.js-report-form').slideUp(slideDuration);
    };

    /**
     * Submit report
     */
    var submitReport = function(e) {
        e.preventDefault();

        var sendurl = this.form.getAttribute('action'),
            form = this.form,
            input = this.form.elements;

        // avoid repeated submits
        $(this).prop('disabled', true);

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
        var documentWidth = getCachedValue('documentWidth');

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
        // invalidate cache
        cache = {};

        initLayout();

    }, 250); // Maximum run of once per 250 milliseconds

    /**
     * Scroll comments list
     */
    var scrollComments = function(e) {
        var direction      = e.target.getAttribute('data-direction'),
            windowTop      = $(window).scrollTop(),
            windowBottom   = windowTop + document.documentElement.clientHeight,
            commentsHeight = getCachedValue('commentsHeight'),
            commentsTop    = getCachedValue('commentsTop'),
            visibleTop     = getCachedValue('visibleTop'),
            visibleBottom  = getCachedValue('visibleBottom'),
            start = visibleTop,
            end = visibleBottom,
            newOffset,
            visibleHeight,
            listHeight;

        // calculate visible height for comments
        if (windowTop > visibleTop) {
            start = windowTop;
        }
        if (windowBottom < visibleBottom) {
            end = windowBottom;
        }

        visibleHeight = Math.round(end - start);

        switch (direction) {
            case 'up':
                // calculate new comments offset
                newOffset = currentOffset + visibleHeight;
                $comments.addClass('show-older-trigger');

                // detect whether we need the newer trigger for another round
                if (newOffset >= 0) {
                    newOffset = 0; // never scroll over the top
                    $comments.removeClass('show-newer-trigger');
                }

                // ensure maximum viewport
                if (windowTop < commentsTop) {
                    $('html, body').animate({
                        scrollTop: Math.floor(commentsTop)
                    }, 1000);
                }

                break;

            default:
                // calculate new comments offset
                newOffset = currentOffset - visibleHeight;
                $comments.addClass('show-newer-trigger');
                listHeight = $commentsBody.prop('scrollHeight'); // same as $commentsActiveList.height()

                // detect whether we need the older trigger for another round
                if (Math.abs(newOffset) + commentsHeight > listHeight) {
                    newOffset = -listHeight + Math.ceil(commentsHeight); // never scroll too far
                    $comments.removeClass('show-older-trigger');
                }
        }

        setCurrentOffset(newOffset);
    };

    /**
     * Ensure visibility of linked comment
     */
    var showComment = function() {
        var anchor = window.location.hash.slice(1), // remove '#'
            target,
            offset;

            if (/^cid-\d/.test(anchor)) {
                target = $(window.location.hash);

                if (! target.length) {
                    return;
                }

                // links from "recommented comments"
                if (! target.is(':visible')) {
                    $commentsTabsHead.find('.tabs__head__tab:first').click();

                    if (paginated) {
                        $('html, body').stop().animate({
                            scrollTop: $commentsTabsHead.offset().top
                        }, 400);

                        offset = $commentsActiveList.offset().top - target.offset().top;

                        if (offset < 0) {
                            offset += getCachedValue('buttonUpHeight');
                        }

                        setCurrentOffset(offset);
                        calculatePagination();
                    } else {
                        $('html, body').stop().animate({
                            scrollTop: target.offset().top
                        }, 500);
                    }
                }
            }
    };

    /**
     * Helper functions
     */
    var getCachedValue = function(key) {
        if (key in cache) {
            return cache[key];
        }

        switch (key) {
            case 'buttonUpHeight':
            case 'commentsHeight':
            case 'commentsTop':
            case 'visibleTop':
            case 'visibleBottom':
                var $buttonUp = $('#js-comments-button-up'),
                    $buttonDown = $('#js-comments-button-down');

                cache.buttonUpHeight = $buttonUp.height();
                cache.commentsHeight = $comments.height() - $commentsBody.position().top;
                cache.commentsTop    = $commentsBody.offset().top;
                cache.visibleTop     = cache.commentsTop + cache.buttonUpHeight;
                cache.visibleBottom  = cache.commentsTop + cache.commentsHeight - $buttonDown.height();
                break;

            case 'documentWidth':
                cache.documentWidth = document.documentElement.clientWidth || document.body.clientWidth || $(document).width();
                break;
        }

        if (key in cache) {
            return cache[key];
        }

        return null;
    };

    var getHiddenProperty = function(element, property) {
        element.css('display', 'block');
        var value = element.prop(property);
        element.css('display', '');

        return value;
    };

    var setCurrentOffset = function(offset) {
        offset = Math.round(offset);
        $commentsActiveList.css('top', offset);
        currentOffset = offset;
    };

    var hideOtherForms = function() {
        $commentsBody.find('form').filter(':visible').slideToggle(slideDuration);
    };

    var generateJSONPNumber = function() {
        return (1361462065627 + Math.floor(Math.random()*101));
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
        $socialServices.on('click', '.js-comments-trigger', toggleComments);
        $commentsBody.on('click', '.js-reply-to-comment', replyToComment);
        $commentsBody.on('click', '.js-report-comment', reportComment);
        $commentsBody.on('click', '.js-cancel-report', cancelReport);
        $commentsBody.on('click', '.js-submit-report', submitReport);
        $comments.on('click', '.js-scroll-comments', scrollComments);
        $comments.on(inputEvent, '.js-required', enableForm);
        $(window).on('resize', updateLayout);
        $(window).on('hashchange', showComment);

        // on document ready: check for url hash to enable anchor links and return urls
        $(function() {
            var anchor = window.location.hash.slice(1);

            if (/^cid-\d/.test(anchor)) {
                toggleComments();

                var target = document.getElementById(anchor) || document.getElementsByName(anchor)[0];

                if (!target) {
                    return;
                }

                $('html, body').stop().animate({
                    scrollTop: $(target).offset().top
                }, 400);
            }
        });

        // handle tab switch: recalculate comment metrics for new comment list
        $commentsTabsHead.on('click', '.tabs__head__tab', function(e) {
            $commentsActiveList = $(e.target.hash);
            currentOffset = parseInt($commentsActiveList.css('top'), 10);
            calculatePagination();
        });

    };

    return {
        init: init
    };

});

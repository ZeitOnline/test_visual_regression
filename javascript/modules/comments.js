/* global console, define, Modernizr */

/**
 * @fileOverview Module for comments
 * @version  0.1
 */
/**
 * comments.js: module for comments
 * @module comments
 */
define(['jquery', 'underscore', 'modules/tabs'], function($, _) {

    var $socialServices = $('#js-social-services'),
        $comments = $('#js-comments'),
        $page = $('#js-page-wrap-inner'),
        $commentsTabsHead = $('#js-comments-tabs-head'),
        $commentsBody = $('#js-comments-body'),
        $commentsActiveList = $('#js-comments-body .tabs__content.is-active .comments__list'),
        DOM_VK_ESCAPE = 27,
        currentOffset = 0,
        slideDuration = 300,
        scrollDuration = 1000, // in sync with CSS animation speed
        paginated = false,
        cache = {},
        startEvent = ('ontouchstart' in window) ? 'touchstart' : 'click',
        inputEvent = ('oninput' in document.createElement('input')) ? 'input' : 'keypress';

    /**
     * comments.js: handles comment pagination
     * @function calculatePagination
     */
    var calculatePagination = function() {
        var commentsCss = getCachedValue('commentsCss');

        $comments.removeClass('show-newer-trigger show-older-trigger');
        paginated = false;

        // handle tablet/desktop size with paginated comments
        if (commentsCss.position === 'absolute') {
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
     * comments.js: reply to comment
     * @function replyToComment
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
     * comments.js: report comment
     * @function reportComment
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
     * comments.js: show form
     * @function showForm
     * @param  {object} form    jQuery object
     * @param  {object} comment jQuery object
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
     * comments.js: cancel report
     * @function cancelReport
     * @param  {object} e event object
     */
    var cancelReport = function(e) {
        e.preventDefault();

        $(this).closest('.js-report-form').slideUp(slideDuration);
    };

    /**
     * comments.js: submit report
     * @function submitReport
     * @param  {object} e event object
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
     * comments.js: enable form submit button
     * @function enableForm
     * @param  {object} e event object
     */
    var enableForm = function() {
        var blank = /^\s*$/.test(this.value);

        $(this.form).find('.button').prop('disabled', blank);
    };

    /**
     * comments.js: toggle comments
     * @function toggleComments
     */
    var toggleComments = function() {
        var $body = $(document.body);

        $body.toggleClass('show-comments');

        // attach event handler function on page, but only for devices without touch support
        // we can not check reliably for real mouse events here, because e.g. Mobile Safari emulates mouse events
        if (! Modernizr.touch) {
            // and only if comments are shown
            if ($body.hasClass('show-comments')) {
                $page.on('mousedown', hideComments);
                $(window).on('keydown', escapeComments);
            } else {
                $page.off('mousedown', hideComments);
                $(window).off('keydown', escapeComments);
            }
        }
    };

    /**
     * comments.js: initialize layout
     * @function initLayout
     */
    var initLayout = function() {
        var commentsCss = getCachedValue('commentsCss');

        if (commentsCss.top === '0px') {
            // on big screens find out how much outside space there is
            var clientWidth = getCachedValue('clientWidth'),
                commentsWidth = clientWidth - $page.outerWidth();

            $comments.css('width', commentsWidth);
        } else {
            // mobile case: show full width comments
            $comments.css('width', '');
        }

        // calculate if we need pagination
        calculatePagination();
    };

    /**
     * comments.js: update layout
     * @function updateLayout
     */
    var updateLayout = _.debounce(function(e) {
        // invalidate cache
        cache = {};

        initLayout();

    }, 250); // Maximum run of once per 250 milliseconds

    /**
     * comments.js: close comments on click outside the comments section
     * @function hideComments
     * @param  {object} e event object
     */
    var hideComments = function(e) {
        var $target = $(e.target),
            triggerClick = $target.closest('.js-comments-trigger').length,
            commentsClick = $target.closest('#js-comments').length;

        if (!triggerClick && !commentsClick) {
            toggleComments();
        }
    };

    /**
     * comments.js: close comments on <ESCAPE>
     * @function escapeComments
     * @param  {object} e event object
     */
    var escapeComments = function(e) {
        // do nothing if there is another key involved
        if (e.altKey || e.shiftKey || e.ctrlKey || e.metaKey) { return; }

        if (e.keyCode === DOM_VK_ESCAPE) {
            toggleComments();
        }
    };

    /**
     * comments.js: scroll comments list
     * @function scrollComments
     * @param  {object} e event object
     */
    var scrollComments = function(e) {
        var direction      = e.target.getAttribute('data-direction'),
            clientHeight   = getCachedValue('clientHeight'),
            windowTop      = $(window).scrollTop(),
            windowBottom   = windowTop + clientHeight,
            commentsHeight = getCachedValue('commentsHeight'),
            commentsTop    = getCachedValue('commentsTop'),
            commentsBottom = getCachedValue('commentsBottom'),
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
                if (windowTop < commentsTop && windowBottom < commentsBottom) {
                    $('html, body').animate({
                        scrollTop: Math.floor(commentsTop)
                    }, scrollDuration);
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

                // ensure maximum viewport
                if (windowTop > commentsTop && windowBottom > commentsBottom) {
                    $('html, body').animate({
                        scrollTop: Math.floor(commentsBottom - clientHeight)
                    }, scrollDuration);
                }
        }

        setCurrentOffset(newOffset);
    };

    /**
     * comments.js: ensure visibility of linked comment
     * @function showComment
     * @param  {object} e      event object
     * @param  {boolean} onload 
     */
    var showComment = function(e, onload) {
        var anchor = window.location.hash.slice(1); // remove '#'

            if (/^cid-\d/.test(anchor)) {
                var target = $(window.location.hash),
                    hidden = target.is(':hidden'),
                    offset;

                if (! target.length) {
                    return;
                }

                if (onload) {
                    toggleComments();
                }

                // links from "recommented comments"
                if (hidden) {
                    $commentsTabsHead.find('.tabs__head__tab:first').click();
                }

                if (hidden || onload) {
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

    //helper functions

    /**
     * comments.js: get cached values
     * @function getCachedValue
     * @param  {string} key
     * @return {object}
     */
    var getCachedValue = function(key) {
        if (key in cache) {
            return cache[key];
        }

        switch (key) {
            case 'buttonUpHeight':
            case 'commentsHeight':
            case 'commentsTop':
            case 'commentsBottom':
            case 'visibleTop':
            case 'visibleBottom':
                var $buttonUp   = $('#js-comments-button-up'),
                    $buttonDown = $('#js-comments-button-down');

                cache.buttonUpHeight = $buttonUp.height();
                cache.commentsHeight = $comments.height() - $commentsBody.position().top;
                cache.commentsTop    = $commentsBody.offset().top;
                cache.commentsBottom = cache.commentsTop + cache.commentsHeight;
                cache.visibleTop     = cache.commentsTop + cache.buttonUpHeight;
                cache.visibleBottom  = cache.commentsTop + cache.commentsHeight - $buttonDown.height();
                break;

            case 'clientWidth':
                cache.clientWidth = document.documentElement.clientWidth || document.body.clientWidth || $(document).width();
                break;

            case 'clientHeight':
                cache.clientHeight = document.documentElement.clientHeight || document.body.clientHeight || $(window).height();
                break;

            case 'commentsCss':
                cache.commentsCss = $comments.css(['top', 'position']);
                break;
        }

        if (key in cache) {
            return cache[key];
        }

        return null;
    };

    /**
     * comments.js: get hidden property
     * @function getHiddenProperty
     * @param  {object} element 
     * @param  {string} property
     * @return {integer}
     */
    var getHiddenProperty = function(element, property) {
        element.css('display', 'block');
        var value = element.prop(property);
        element.css('display', '');

        return value;
    };

    /**
     * comments.js: set current offset
     * @function setCurrentOffset
     * @param  {integer} offset 
     */
    var setCurrentOffset = function(offset) {
        offset = Math.round(offset);
        $commentsActiveList.css('top', offset);
        currentOffset = offset;
    };

    /**
     * comments.js: hide other forms
     * @function hideOtherForms
     */
    var hideOtherForms = function() {
        $commentsBody.find('form').filter(':visible').slideToggle(slideDuration);
    };

    /**
     * comments.js: generate jsonp number
     * @function generateJSONPNumber
     * @return {integer}
     */
    var generateJSONPNumber = function() {
        return (1361462065627 + Math.floor(Math.random()*101));
    };

    /**
     * comments.js: initialize
     * @function init
     */
    var init = function() {

        if (! $comments.length) {
            return;
        }

        initLayout();

        // register event handlers
        $socialServices.on(startEvent, '.js-comments-trigger', toggleComments);
        $commentsBody.on(startEvent, '.js-reply-to-comment', replyToComment);
        $commentsBody.on(startEvent, '.js-report-comment', reportComment);
        $commentsBody.on(startEvent, '.js-cancel-report', cancelReport);
        $commentsBody.on(startEvent, '.js-submit-report', submitReport);
        $comments.on(startEvent, '.js-scroll-comments', scrollComments);
        $comments.on(inputEvent, '.js-required', enableForm);
        $(window).on('resize', updateLayout);
        $(window).on('hashchange', showComment);

        // on document ready: check for url hash to enable anchor links and return urls
        $(function(e) {
            // setTimeout needed for FF bug with linked element inside block having overflow:hidden
            window.setTimeout(function(){
               showComment(e, true);
               $comments.addClass('comments--animated');
           }, 1);
        });

        // handle tab switch: recalculate comment metrics for new comment list
        $commentsTabsHead.on('click', '.tabs__head__tab', function(e) {
            if (e.target.hash === '#tab2' && 'pushState' in history) {
                history.pushState('', document.title, location.pathname + location.search);
            }

            $commentsActiveList = $(e.target.hash);
            currentOffset = parseInt($commentsActiveList.css('top'), 10);
            calculatePagination();
        });

    };

    return {
        init: init
    };

});

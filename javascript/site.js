/**
 * @fileOverview zeit.web.site module
 * @version  0.1
 */

// required plain vanilla JS programs here
require([
    'web.core/images',
    'web.site/nav',
], function( images, nav ) {
    images.init();
    nav.init();
});

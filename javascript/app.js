/* globals require */

require.config({
  paths: {
    "jquery": "libs/jquery-1.10.2.min"
  }
});

require(['modules/fontloader',
         'modules/breadcrumbs',
         'modules/main-nav'], function(fontloader,
                                       breadcrumbs,
                                       main_nav) {
  fontloader.init();
  breadcrumbs.init();
  main_nav.init();
});
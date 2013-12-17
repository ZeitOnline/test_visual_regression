/* globals require */

require.config({
	paths: {
    "jquery": "libs/jquery-1.10.2.min"
	},
	shim: {
		'modules/plugins/jquery.switchvideo': {
			deps: [ 'jquery' ],
			exports: 'jQuery.fn.switchVideo'
		}
	}
});

require(['modules/fontloader', 'modules/breadcrumbs', 'modules/tabs', 'modules/comments', 'modules/main-nav', 'modules/adloader', 'modules/plugins/jquery.switchvideo'],
  function(fontloader, breadcrumbs, tabs, comments, main_nav, adloader) {
    fontloader.init();
    main_nav.init();
    breadcrumbs.init();
    tabs.init();
    comments.init();
    adloader.init();
		$( "figure[data-video]" ).switchVideo();
});
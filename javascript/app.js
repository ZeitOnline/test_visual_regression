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

require(['modules/fontloader', 'modules/breadcrumbs', 'modules/comments', 'modules/main-nav', 'modules/plugins/jquery.switchvideo'],
  function(fontloader, breadcrumbs, comments, main_nav) {
    fontloader.init();
    main_nav.init();
    breadcrumbs.init();
    comments.init();
		$( "figure[data-video]" ).switchVideo();
});
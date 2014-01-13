/* globals require */

require.config({
	paths: {
		"jquery": "libs/jquery-1.10.2.min",
		"sjcl": "libs/sjcl"
	},
	shim: {
		'modules/plugins/jquery.switchvideo': {
			deps: [ 'jquery' ],
			exports: 'jQuery.fn.switchVideo'
		}
	}
});

require(['modules/fontloader', 'modules/breadcrumbs', 'modules/main-nav', 'modules/images', 'sjcl', 'modules/plugins/jquery.switchvideo'],
  function( fontloader, breadcrumbs, main_nav, images ) {
    fontloader.init();
    main_nav.init();
    breadcrumbs.init();
    images.init();
		$( "figure[data-video]" ).switchVideo();
});
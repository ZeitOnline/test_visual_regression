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

require(['modules/fontloader', 'modules/breadcrumbs', 'modules/plugins/jquery.switchvideo'],
	function( fontloader, breadcrumbs ) {
		fontloader.init();
		breadcrumbs.init();

		if( $( "figure[data-video]" ).size() > 0 ){
			$( "figure[data-video]" ).switchVideo();
		}
});
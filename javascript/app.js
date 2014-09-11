/* globals require, define, console */

/**
 * @fileOverview Require.js Config File
 * @version  0.1
 */

// configuration section for require js
require.config({
	// Require.js allows us to configure shortcut alias
	// e.g. if you'll require jQuery later, you can refer to it as 'jquery'
	paths: {
		"jquery": "libs/jquery-1.10.2.min",
		"sjcl": "libs/sjcl",
		"underscore": "libs/underscore-min",
		"bxSlider": "libs/jquery.bxslider",
		"jquery-bridget/jquery.bridget": "libs/packery.pkgd.min",
		"esiparser": "libs/esiparser"
	},
	// a shim is need for jQuery Plugins to load
	// add the name or path and an array of required scripts
	shim: {
		"bxSlider" : ['jquery'],
		"modules/plugins/jquery.inlinegallery": ["bxSlider", "jquery"],
		'modules/plugins/jquery.switchvideo': ["jquery"],
		'modules/plugins/jquery.backgroundvideo': ['jquery'],
		'modules/plugins/jquery.enablepopups': ['jquery'],
		'modules/plugins/jquery.animatescroll': ['jquery'],
		'modules/plugins/jquery.parseesi': ['jquery','esiparser'],
		'sjcl': {
			exports: 'sjcl'
		},
		'libs/freewall': {
			deps: ['jquery'],
			exports: 'freewall'
		}
	}
});

// required plain vanilla ja programs here
// the order in the array and the function names have to correlate
// which is quite disturbing in my book…
require([
	'modules/errors',
	'modules/fontloader_body',
	'modules/main-nav',
	'modules/tabs',
	'modules/comments',
	'modules/sharing',
	'modules/cards',
	'modules/copyrights',
	'modules/images',
	'modules/photocluster',
], function( errors, fontloader_body, main_nav, tabs, comments, sharing, cards, copyrights, images, photocluster) {
	errors.init();
	fontloader_body.init();
	main_nav.init();
	tabs.init();
	comments.init();
	sharing.init();
	cards.init();
	copyrights.init();
	photocluster.init();
	images.init();
});

// add required jQuery-Plugins that are writte with AMD header here
// make a shim of them first
// plugins that require plugins need to make this requirement in the shim-section of config
require([
	'modules/plugins/jquery.inlinegallery',
	'modules/plugins/jquery.switchvideo',
	'modules/plugins/jquery.backgroundvideo',
	'modules/plugins/jquery.enablepopups',
	'modules/plugins/jquery.animatescroll',
	'modules/plugins/jquery.parseesi'
], function () {
	$( ".inline-gallery" ).inlinegallery();
	$( "figure[data-video]" ).switchVideo();
	$( "div[data-backgroundvideo]" ).backgroundVideo();
	$( "a.js-has-popup" ).enablePopups();
	$( "main" ).animateScroll({selector: '.js-scroll'});
	$( "div[data-type = 'esi-content']" ).parseEsi();
});

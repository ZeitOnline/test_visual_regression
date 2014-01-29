/* globals require, define, console */

// configuration section for require js
require.config({
	// Require.js allows us to configure shortcut alias
	// e.g. if you'll require jQuery later, you can refer to it as 'jquery'
	paths: {
		"jquery": "libs/jquery-1.10.2.min",
		"sjcl": "libs/sjcl",
		"underscore": "libs/underscore-min",
		"bxSlider": "libs/jquery.bxslider"
	},
	// a shim is need for jQuery Plugins to load
	// add the name or path and an array of required scripts
	shim: {
		"bxSlider" : ['jquery'],
		"modules/plugins/jquery.inlinegallery": ["bxSlider","jquery"]
	}
});

require(['modules/plugins/jquery.inlinegallery'], function() {
	$( ".inline-gallery" ).inlinegallery();
});
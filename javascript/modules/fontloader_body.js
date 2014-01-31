/* global console, define */

define(['jquery'], function() {
	var fl = window.FontLoader;
	var append_css = function(style) {
		// create a style tag in the <head> filled with raw font-face declarations
		var style_tag = window.document.createElement( "style" );
		style_tag.innerHTML = style;
		if( fl.inject_ref && fl.inject_ref.parentNode ) {
			fl.inject_ref.parentNode.insertBefore( style_tag, fl.inject_ref );
		}
	};

	var fetch_css = function(path, identifier, font_data) {
		// if we already have font_data (from localstorage), make use of it immediately
		if (font_data && font_data.length > 0) {
			append_css(font_data);
		} else {
			// nope, we don’t: let’s fetch it asynchronously from the server
			$.ajax({
				url: path,
				success: function (ajaxed_style) {
					// we’ve got the fonts, store them in localstorage and apply them
					localStorage.setItem(fl.storage_base_string + identifier, ajaxed_style);
					append_css(ajaxed_style);
				}
			});
		}
	};

	var load_fonts = function() {
		var scheduled_fonts = [];
		for (var i in fl.font_dictionary) {
			if (i) {
				var pack = fl.font_dictionary[i];
				// apply fonts if no selector present or selector returns at least one element
				if (!pack.selector || document.querySelectorAll(pack.selector).length >= 1) {
					pack.data = localStorage.getItem(fl.storage_base_string + pack.identifier);
					// if pack has priority or data is already in localstorage: apply immediately
					if (pack.has_priority || pack.data) {
						// drop it in as fast as possible
						fetch_css(pack.path, pack.identifier, pack.data);
					} else {
						// schedule for later lazy loading
						scheduled_fonts.push(fl.font_dictionary[i]);
					}
				}
			}
		}
		// lazy load fonts at last
		window.onload = function() {
			for (var i in scheduled_fonts) {
				if (i) {
					fetch_css(scheduled_fonts[i].path, scheduled_fonts[i].identifier);
				}
			}
		};
	};

	// only load webfont css when we have a good guesstimate that the browser will support woff
	var init = function() {
		if (!fl.is_old_browser && !fl.fonts_loaded) {
			load_fonts();
		}
	};

	return {
		init: init
	};

});
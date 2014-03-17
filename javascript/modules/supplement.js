/* global console, define, alert, postscribe */

define(['postscribe', 'jquery'], function() {

	// list of possible ads
	// guess we need this configuration somewhere global accessible
	var ads = {
		// top banner supplies: leaderboard, wallpaper and fireplace
		topbanner: {
			url: 'http://ad.de.doubleclick.net/adj/',
			fragment: 'zeitonline/zolmz',
			dcopt: 'ist',
			tile: 1,
			size: '728x90',
			keywords: ['iqadtile1', 'zeitonline', 'zeitmz']
		},
		// top banner supplies: leaderboard
		topbanner_no_fp_no_wp: {
			url: 'http://ad.de.doubleclick.net/adj/',
			fragment: 'zeitonline/zolmz',
			dcopt: 'ist',
			tile: 1,
			size: '728x90',
			keywords: ['iqadtile1', 'zeitonline', 'zeitmz', 'noiqdfireplace', 'noiqdwallpaper']
		},
		// scyscraper ad (hidden if wallpaper or fireplace is given)
		skyscraper: {
			url: 'http://ad.de.doubleclick.net/adj/',
			fragment: 'zeitonline/zolmz',
			tile: 2,
			size: '120x600',
			keywords: ['iqadtile2', 'zeitonline', 'zeitmz']
		},
		mobile: {
			ismobile: true,
			callback: function() {
				var sas_pageid = '54114/391248',
					sas_formatid = 13500,
					sas_target = '';
				if( typeof window.sasmobile === 'function') {
					window.sasmobile(sas_pageid,sas_formatid,sas_target);
				}
			}
		},
		medrec_8: {
			url: 'http://ad.de.doubleclick.net/adj/',
			fragment: 'zeitonline/zeitmz',
			tile: 8,
			size: '300x250,300x600,300x100',
			keywords: ['iqadtile8', 'zeitmz', 'noiqdband']
		},
		medrec_10: {
			url: 'http://ad.de.doubleclick.net/adj/',
			fragment: 'zeitonline/zeitmz',
			tile: 10,
			size: '300x250,300x100',
			keywords: ['iqadtile10', 'zeitmz', 'noiqdband']
		}
	},
	// configuration of ad places aka. slots
	// one place can own n ads, differing by screen estate size
	places = {
		topbanner: [{
			// desktop full
			div_id: 'iqadtile1',
			min_width: 981,
			min_height: 0,
			ad: ads.topbanner
		},
		{
			// desktop but narrow
			div_id: 'iqadtile1',
			min_width: 728,
			max_width: 980,
			min_height: 0,
			ad: ads.topbanner_no_fp_no_wp
		}],
		mobile_topbanner: [{
			// the one and only mobile ad
			div_id: 'sas_13500',
			div_class: 'ad__leaderboard--mobile',
			max_width: 727,
			min_width: 320,
			min_height: 0,
			ad: ads.mobile
		}],
		skyscraper: [{
			div_id: 'iqadtile2',
			min_width: 728,
			min_height: 0,
			ad: ads.skyscraper
		}],
		medrec_8: [{
			div_class: "ad__rec",
			div_id: 'iqadtile8',
			min_width: 720,
			min_height: 0,
			ad: ads.medrec_8
		}],
		medrec_10: [{
			div_class: "ad__rec",
			div_id: 'iqadtile10',
			min_width: 720,
			min_height: 0,
			ad: ads.medrec_10
		}]
	},
	/**
	 * [build_tag description]
	 * @param  {[type]} creative
	 * @param  {[type]} elem
	 * @return {[type]}
	 */
	build_tag = function( creative, elem ) {
		var adclass = creative.div_class || "",
		adid = creative.div_id || "",
		tag = '<div class="'+ adclass +'" id="'+ adid +'">%tag%</div>',
		scripttext = '';

		if( creative.ad.ismobile === true ) {
			tag = tag.replace('%tag%', "");
			$(tag).appendTo($(elem));
			creative.ad.callback.call();
			return false;
		} else {
			scripttext += '<script src="';
			scripttext += creative.ad.url;
			scripttext += creative.ad.fragment;
			if( typeof creative.ad.dcopt !== 'undefined' ) {
				scripttext += ';dcopt=' + creative.ad.dcopt;
			}
			scripttext += ';tile=' + creative.ad.tile;
			scripttext += ';' + window.n_pbt;
			scripttext += 'sz=' + creative.ad.size;
			scripttext += ';kw=' + creative.ad.keywords.join(",");
			scripttext += ',' + window.iqd_TestKW;
			scripttext += ';ord=' + window.IQD_varPack.ord;
			scripttext += '?" type="text/javascript"><\/script>';
			tag = tag.replace('%tag%', scripttext);
			return tag;
		}
	},
	/**
	 * [prepare_slot description]
	 * @param  {[type]} place
	 * @param  {[type]} elem
	 * @return {[type]}
	 */
	prepare_slot = function( place, elem ) {
		var slot = places[place], ad, _i, _len, _ref, tag, result;
		_ref = slot.slice(0).reverse();
		for ( _i = 0, _len = _ref.length; _i < _len; _i++ ) {
			ad = _ref[_i];
			if( !ad.max_width ){
				ad.max_width = 5000;
			}
			if( window.innerWidth >= ad.min_width &&
				window.innerHeight >= ad.min_height &&
				window.innerWidth <= ad.max_width ) {
				// build applicable ad
				return build_tag( ad, elem );
			} else {
				result = false;
			}
		}
		return result;

	},
	/**
	 * [init description]
	 * @return {[type]}
	 */
	init = function() {
		$(".iqdplace").each(function() {
			var place = $(this).data('place'),
				adtext = prepare_slot( place, this );
			if ( adtext ) {
				postscribe( this, adtext);
			}
		});
		return true;
	};

	return {
		init: init
	};

});
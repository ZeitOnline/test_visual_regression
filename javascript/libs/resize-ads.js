/*
*
* resize-ads.js
* loads ads in the needed size depending on screen estate
*
*/
var resizeAds = function( win, doc ) {

	// privates
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
		// scyscraper ad (hidden if wallpaper or fireplace is given)
		skyscraper: {
			url: 'http://ad.de.doubleclick.net/adj/',
			fragment: 'zeitonline/zolmz',
			tile: 2,
			size: '120x600',
			keywords: ['iqadtile2', 'zeitonline', 'zeitmz']
		}
	},
	places = {
		topbanner: {
			active_class: null,
			active_ad: null,
			ads: [
				{
					div_class: 'iqadtile1',
					min_width: 728,
					min_height: 0,
					ad: ads.topbanner
				}
			]
		},
		skyscraper: {
			active_class: null,
			active_ad: null,
			ads: [
				{
					div_class: 'iqadtile2',
					min_width: 728,
					min_height: 0,
					ad: ads.skyscraper
				}
			]
		}
	},
	prepare_slot = function( slot ) {
		var ad, _i, _len, _ref, _results;
		_ref = slot.ads.slice(0).reverse();
		_results = [];
				
		for(_i = 0, _len = _ref.length; _i < _len; _i++ ){
			ad = _ref[_i];
			if( !ad.max_width ){
				ad.max_width = 5000;
			}
			if (window.innerWidth >= ad.min_width &&
				window.innerHeight >= ad.min_height &&
				window.innerWidth <= ad.max_width) {
					slot.active_class = ad.div_class;
					slot.active_ad = ad['ad'];
					return slot;
			} else {
				_results.push(void 0);
			}
		}
		return _results;
	};

	return {
		print_ad_place: function( place ) {
			var slot = prepare_slot( places[place] );
			console.debug(slot);
			var div = '<div class="' + slot.active_class + '">%1</div>';
			
		}
	};

}( window, document );


//define when to risze ads

// (function() {

// 	var prepare_slot;
    
// 	window.ad_slots = {
// 		//leaderboard
// 		leaderboard: {
// 			active_class: null,
// 			active_text: '',
// 			ads: [
// 					//full size leaderboard
// 					{
// 						div_class: "ad__leaderboard--full",
// 						min_width: 728,
// 						min_height: 0,
// 						text: "Leaderboard"
// 					},
// 					//mobile banner
// 					{
// 						div_class: "ad__leaderboard--mobile",
// 						min_width: 320,
// 						max_width: 728,
// 						min_height: 0,
// 						text: "Mobile Banner"
// 					}
// 				]
// 			},
// 		//fireplace top area
// 		fp_top: {
// 			active_class: null,
// 			active_text: '',
// 			ads: [
// 					//top banner
// 					{
// 						div_class: "ad__fp--top",
// 						min_width: 1245,
// 						min_height: 0,
// 						text: "Fireplace Top"
// 					}
// 			]
// 		},
// 		//fireplace left area
// 		fp_left: {
// 			active_class: null,
// 			active_text: '',
// 			ads: [
// 					//left banner
// 					{
// 						div_class: "ad__fp--left",
// 						min_width: 1245,
// 						min_height: 600,
// 						text: "Fireplace Left"
// 					}
// 			]
// 		},
// 		//fireplace right area
// 		fp_right: {
// 			active_class: null,
// 			active_text: '',
// 			ads: [
// 					//right banner
// 					{
// 						div_class: "ad__fp--right",
// 						min_width: 1245,
// 						min_height: 600,
// 						text: "Fireplace Right"
// 					}
// 			]
// 		},
// 		//rectangle
// 		rec: {
// 			active_class: null,
// 			active_text: '',
// 			ads: [
// 					//medium rectangle
// 					{
// 						div_class: "ad__rec",
// 						min_width: 720,
// 						min_height: 0,
// 						text: '<script src="http://ad.doubleclick.net/N183/adj/zeitmz/homepage;tile=8;' + window.n_pbt + ';sz=300x250,300x600,300x100;kw=iqadtile8,zeitmz,noiqdband,'+ window.iqd_TestKW +';ord=' + window.ord + '?" type="text/javascript"><\/script>'
// 					}
// 			]
// 		}
// 	};
      
// 	//define slot ads
// 	prepare_slot = function(slot) {

// 		var ad, _i, _len, _ref, _results;
// 		_ref = slot.ads.slice(0).reverse();
// 		_results = [];
		
// 		for(_i = 0, _len = _ref.length; _i < _len; _i++ ){

// 			ad = _ref[_i];

// 			if( !ad.max_width ){
//               ad.max_width = 5000;
//             }

//             if (window.innerWidth >= ad.min_width && window.innerHeight >= ad.min_height && window.innerWidth <= ad.max_width) {
//                 slot.active_class = ad.div_class;
//                 slot.active_text = ad.text;
//                 break;
//             } else {
//               _results.push(void 0);
//             }

//           }

//           return _results;
// 	};
     
//     //call slot ads
// 	prepare_slot(window.ad_slots.fp_top);
// 	prepare_slot(window.ad_slots.fp_left);
// 	prepare_slot(window.ad_slots.fp_right);
// 	prepare_slot(window.ad_slots.rec);
// 	prepare_slot(window.ad_slots.leaderboard);
      
// }).call(this);

(function() {
        var prepare_slot;
    
        window.ad_slots = {
          leaderboard: {
            active_class: null,
            active_text: '',
            ads: [
              {
                div_class: "ad__leaderboard--full",
                min_width: 728,
                min_height: 0,
                text: "Leaderboard"
              },
              {
                div_class: "ad__leaderboard--mobile",
                min_width: 320,
                max_width: 728,
                min_height: 0,
                text: "Mobile Banner"
              }
            ]
          },
          fp_top: {
            active_class: null,
            active_text: '',
            ads: [
              {
                div_class: "ad__fp--top",
                min_width: 1400,
                min_height: 0,
                text: "Fireplace Top"
              }
            ]
          },
          fp_left: {
            active_class: null,
            active_text: '',
            ads: [
              {
                div_class: "ad__fp--left",
                min_width: 1400,
                min_height: 600,
                text: "Fireplace Left"
              }
            ]
          },
          fp_right: {
            active_class: null,
            active_text: '',
            ads: [
              {
                div_class: "ad__fp--right",
                min_width: 1400,
                min_height: 600,
                text: "Fireplace Right"
              }
            ]
          },
          rec: {
            active_class: null,
            active_text: '',
            ads: [
              {
                div_class: "ad__rec",
                min_width: 720,
                min_height: 0,
                text: "Rectangle"
              }
            ]
          }
        };
      
        prepare_slot = function(slot) {
          var ad, _i, _len, _ref, _results;
          _ref = slot.ads.slice(0).reverse();
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            ad = _ref[_i];

            if( !ad.max_width ){
              ad.max_width = 5000; 
            }

            if (window.innerWidth >= ad.min_width && window.innerHeight >= ad.min_height && window.innerWidth <= ad.max_width) {
                slot.active_class = ad.div_class;
                slot.active_text = ad.text;
                break;
            } else {
              _results.push(void 0);
            }
          }
          return _results;
        };
     
        prepare_slot(window.ad_slots.fp_top);
        prepare_slot(window.ad_slots.fp_left);
        prepare_slot(window.ad_slots.fp_right);
        prepare_slot(window.ad_slots.rec);
        prepare_slot(window.ad_slots.leaderboard);
      
      }).call(this);
      

(function() {
        var prepare_slot;
      
        window.ad_slots = {
          top: {
            active_url: "",
            ads: [
              {
                url: "./adserver/top-banner-s.js",
                min_width: 320,
                min_height: 0
              }, {
                url: "./adserver/top-banner-m.js",
                min_width: 728,
                min_height: 0
              }
            ]
          },
          sidebar: {
            active_url: "",
            ads: [
              {
                url: "./adserver/sidebar-banner-s.js",
                min_width: 320,
                min_height: 150
              }, {
                url: "./adserver/sidebar-banner-m.js",
                min_width: 320,
                min_height: 400
              }, {
                url: "./adserver/sidebar-banner-l.js",
                min_width: 320,
                min_height: 700
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
            if (window.innerWidth >= ad.min_width && window.innerHeight >= ad.min_height) {
              slot.active_url = ad.url;
              break;
            } else {
              _results.push(void 0);
            }
          }
          return _results;
        };
      
        prepare_slot(window.ad_slots.top);
      
        prepare_slot(window.ad_slots.sidebar);
      
      }).call(this);
      

(function() {
        var prepare_slot;
    
        window.ad_slots = {
          top: {
            active_class: "",
            ads: [
              {
                div_class: "ad__top-banner-s",
                min_width: 320,
                min_height: 0
              }, {
                div_class: "ad__top-banner-m",
                min_width: 940,
                min_height: 0
              }
            ]
          },
          sidebar: {
            active_class: "",
            ads: [
              {
                div_class: "ad__sidebar-banner-s",
                min_width: 320,
                min_height: 150
              }, {
                div_class: "ad__sidebar-banner-m",
                min_width: 320,
                min_height: 400
              }, {
                div_class: "ad__sidebar-banner-l",
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
              slot.active_class = ad.div_class;
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
      
{% macro wrapper_handling( obj ) -%}

<!-- wrapper handling -->
<script type="text/javascript">

    //reads cookie
    function getCookie( c_name ) {
        var c_value = document.cookie;
        var c_start = c_value.indexOf(' ' + c_name + '=');

        if ( c_start === -1 ) {
            c_start = c_value.indexOf(c_name + '=');
        }
        if ( c_start === -1 ) {
            c_value = null;
        } else {
            c_start = c_value.indexOf( '=', c_start ) + 1;
            var c_end = c_value.indexOf( ';', c_start );
            if ( c_end === -1 ) {
              c_end = c_value.length;
            }
            c_value = unescape( c_value.substring( c_start,c_end ));
        }
        return c_value;
    }

    // build global wrapper object which will be called from within webview
    // most of the functions here are provided by sevenval
    // as the wrapper app will call them with the wrapper namespace
    // be very careful with renaming, function names have to stick like this
    window.wrapper = {
        // provide ressort
        getRessort: function() {
            var ressort = '{{ obj.ressort }}',
                sub_ressort = '{{ obj.sub_ressort }}';

            if( sub_ressort != '' ){
                ressort = sub_ressort;
            }

            if( ressort == 'lebensart' ){
                return  'Zeit Magazin';
            }else{
                return ressort.charAt(0).toUpperCase() + ressort.slice(1);
            }
        },
        // hide zmo navi header
        hideZMOHeader: function( $nav ){
            $nav.setAttribute("style","display: none");
        },
        //set margin for native bar
        setHeaderMargin: function( _density_independant_pixels ) {

            var $nav = document.getElementsByClassName( 'main-nav' )[0],
                $page = document.getElementsByClassName( 'page-wrap--inner' )[0],
                $spacer = document.createElement( 'header' );

            this.hideZMOHeader( $nav );

            // default: no cookie present and no change requested
            var hm = 0;

            // user has already set header margin
            if (getCookie( 'zeitwrapper_hm' )) {
                hm = getCookie( 'zeitwrapper_hm' );
            }

            // user requested a change header margin
            if (_density_independant_pixels !== null && typeof(_density_independant_pixels) !== 'object' ) {
                hm = _density_independant_pixels;
            }

            //prepare spacer
            $spacer.setAttribute( 'id', 'wrapper_spacer_header');
            $spacer.setAttribute( 'style', 'height:' + hm + 'px' );

            // set and save settings if in valid scope
            $page.insertBefore( $spacer, $nav );
            document.cookie = 'zeitwrapper_hm=' + hm +'; expires=Thu, 31 Dec 2099 23:59:59 UTC; path=/';
        }
    };
</script>
{% endmacro %}

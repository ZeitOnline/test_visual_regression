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

{% macro adplace_adctrl(banner, view) -%}
    {{ caller() }}
    <div id="iqadtile{{ banner.tile }}" class="ad-{{ banner.name }} ad-{{ banner.name }}--on-{{ pagetype }}" data-ad_width="{{ banner.noscript_width_height[0] }}" data-ad_minwidth="{{ banner.min_width }}">
        {% if banner.label -%}
        <div class="ad-{{ banner.name }}__label">{{ banner.label }}</div>
        {% endif -%}
        <div class="ad-{{ banner.name }}__inner">
            <script type="text/javascript">
                 AdController.render('iqadtile{{ banner.tile }}');
            </script>
        </div>
    </div>
{% endmacro %}

{% macro adplace_oldschoolish(banner, view) -%}
    {{ caller() }}
    {% set kw = 'iqadtile' ~ banner.tile ~ ',' ~ view.adwords|join(',') -%}
    {% set pagetype = 'centerpage' if 'centerpage' in view.banner_channel else 'article' -%}
    <!-- Bannerplatz: "{{banner.name}}", Tile: {{banner.tile}} -->
    <div id="iqadtile{{ banner.tile }}" class="ad-{{ banner.name }} ad-{{ banner.name }}--on-{{ pagetype }}" data-ad_width="{{ banner.noscript_width_height[0] }}" data-ad_minwidth="{{ banner.min_width }}">
        {% if banner.label -%}
        <div class="ad-{{ banner.name }}__label">{{ banner.label }}</div>
        {% endif -%}
        <div class="ad-{{ banner.name }}__inner">
            <script type="text/javascript">
                if (
                    window.ZMO.clientWidth >= {{ banner.min_width|default(0) }}
                    {% if banner.tile == 2 %}
                    && window.ZMO.clientWidth != window.ZMO.mobileWidth
                    {% endif %}
                ) {
                    document.write('<script src="http://ad.de.doubleclick.net/adj/zeitonline/{{ view.banner_channel }}{% if banner.dcopt %};dcopt={{ banner.dcopt }}{% endif %};tile={{ banner.tile }};' + n_pbt + ';sz={{ banner.sizes|join(',') }};kw={{ kw }},' + iqd_TestKW {% if banner.diuqilon %}+ window.diuqilon {% endif %}+ ';ord=' + IQD_varPack.ord + '?" type="text/javascript"><\/script>');
                }
            </script>
            <noscript>
            <div>
                <a href="http://ad.de.doubleclick.net/jump/zeitonline/{{ view.banner_channel }};tile={{ banner.tile }};sz={{ banner.sizes|join(',') }};kw={{ kw }};ord=123456789?" rel="nofollow">
                    <img src="http://ad.de.doubleclick.net/ad/zeitonline/{{ view.banner_channel }};tile={{ banner.tile }};sz={{ banner.sizes|join(',') }};kw={{ kw }};ord=123456789?" width="{{ banner.noscript_width_height[0] }}" height="{{ banner.noscript_width_height[1] }}" alt="">
            </a></div>
            </noscript>
        </div>
    </div>
{%- endmacro %}

{% macro adplace_middle_mobile(item) -%}
    {% if item.tile == 7 -%}
    <!-- only integrate onces as equivalent to desktop tile 7 -->
        <div class="iqd-mobile-adplace iqd-mobile-adplace--middle">
            <div id="sas_13557"></div>
        </div>
    {%- endif %}
{%- endmacro %}

{% macro adplace(banner, view) -%}
    {% if view.context.advertising_enabled -%}
        {% if view.deliver_ads_oldschoolish %}
            {% call adplace_oldschoolish(banner, view) -%}
                <!-- tile: {{ banner.tile }} oldschoolish -->
            {%- endcall %}
        {% else %}
            {% call adplace_adctrl(banner, view) -%}
                <!-- tile: {{ banner.tile }} adctrl -->
            {%- endcall %}
        {% endif %}
    {% endif -%}
{%- endmacro %}

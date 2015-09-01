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

            var spacerId = 'wrapper_spacer_header',
                $nav = document.getElementById( 'js-main-nav' ),
                $page = document.getElementById( 'js-page-wrap-inner' ),
                $spacer = document.getElementById( spacerId );

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

            if ( ! $spacer ) {
                // prepare spacer
                $spacer = document.createElement( 'header' );
                $spacer.setAttribute( 'id', spacerId);
                $page.insertBefore( $spacer, $nav );
            }

            // set and save settings if in valid scope
            $spacer.setAttribute( 'style', 'height:' + hm + 'px' );
            document.cookie = 'zeitwrapper_hm=' + hm +'; expires=Thu, 31 Dec 2099 23:59:59 UTC; path=/';
        }
    };
</script>
{% endmacro %}

{% macro adplace_adctrl(banner, view, mobile) -%}
    {{ caller() }}
    {% set pagetype = 'centerpage' if 'centerpage' in view.banner_channel else 'article' -%}
    {% set operator = '<=' if mobile else '>' %}
    {% set type = 'mobile' if mobile else 'desktop' %}
    {% set scriptname = 'ad-%s-%s' | format(type, banner.tile) %}
    <div>
        <script type="text/javascript" id="{{ scriptname }}">
            if (
                typeof AdController !== 'undefined'
                {% if type == 'desktop' and banner.tile == 2 %}
                && ZMO.clientWidth > ZMO.sideAdMinWidth 
                {% endif %}
                && ZMO.clientWidth {{ operator | safe }} ZMO.mobileWidth
                ) {
                if( ! document.getElementById( "iqadtile{{ banner.tile }}" ) ) {
                    var elem = document.createElement('div');
                    elem.id = "iqadtile{{ banner.tile }}";
                    elem.className = "ad ad-{{ type }} ad-{{type}}--{{ banner.tile }} ad-{{type}}--{{ banner.tile }}-on-{{ pagetype }}";
                    elem.setAttribute('data-banner-type', '{{ type }}');
                    {% if banner.label and not(mobile) -%}
                        var label = document.createElement('span');
                        label.className = "ad__label";
                        label.textContent = "{{ banner.label }}";
                        elem.appendChild(label);
                    {% endif -%}
                    document.getElementById('{{ scriptname }}').parentNode.appendChild(elem);
                    AdController.render('iqadtile{{ banner.tile }}');
                    if (console && typeof console.info === 'function') {
                        console.info('AdController ' + AdController.VERSION + ' tile {{ banner.tile }} {{ type }}')
                    }
                }
            }
        </script>
    </div>
{% endmacro %}

{% macro adplace_middle_mobile(banner, view, mobile=True) -%}
    {% if banner.tile == 7 -%}
        {% call adplace_adctrl(banner, view, mobile) -%}
            <!-- tile: {{ banner.tile }} {{ 'mobile' if mobile else 'desktop'}} adctrl -->
        {%- endcall %}
    {%- endif %}
{%- endmacro %}

{% macro adplace(banner, view, mobile=False) -%}
    {% if view.context.advertising_enabled -%}
        {% call adplace_adctrl(banner, view, mobile) -%}
            <!-- tile: {{ banner.tile }} {{ 'mobile' if mobile else 'desktop'}} adctrl -->
        {%- endcall %}
    {% endif -%}
{%- endmacro %}

{% macro content_ad_article(view) -%}
    {% if view.context.advertising_enabled -%}
    <div id="iq-artikelanker"></div>
    {% endif -%}
{%- endmacro %}


{% macro use_svg_icon(name, class, request) -%}
    <svg class="{{ class }}" role="img" aria-labelledby="title">
        <use xlink:href="{{ request.asset_url('css/web.site/icons.svg') }}#svg-{{ name }}"></use>
    </svg>
{%- endmacro %}


{% macro insert_responsive_image(image, image_class, page_type) %}

    {% set alt = ''%}
    {% set title = ''%}

    {% if image.alt %}
        {% set alt = image.alt %}
        {% set title = image.title %}
    {% elif image.attr_alt %}
        {% set alt = image.attr_alt %}
        {% set title = image.attr_title %}
    {% endif %}

    {% if image %}
        <!--[if gt IE 8]><!-->
            <noscript data-src="{{ image | default_image_url }}">
        <!--<![endif]-->
        {% if page_type == 'article' and image.href %}
            <a href="{{ image.href }}">
        {% endif %}
                <img alt="{{ alt }}" {% if title %}title="{{ title }}" {% endif %}class="{{ image_class | default('', true) }} figure__media" src="{{ image | default_image_url }}" data-ratio="{{ image.ratio }}">
        {% if page_type == 'article' and image.href %}
            </a>
        {% endif %}
        <!--[if gt IE 8]><!-->
            </noscript>
        <!--<![endif]-->
    {% endif %}
{% endmacro %}

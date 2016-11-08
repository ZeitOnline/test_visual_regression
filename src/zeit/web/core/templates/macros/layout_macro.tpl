{% macro adplace(banner, view, mobile=False) -%}
  {% if view.advertising_enabled %}
    <!-- tile: {{ banner.tile }} {{ 'mobile' if mobile else 'desktop'}} adctrl -->
    {% set pagetype = 'centerpage' if 'centerpage' in view.banner_channel else 'article' -%}
    {% set operator = '' if mobile else '!' %}
    {% set type = 'mobile' if mobile else 'desktop' %}
    {% set scriptname = 'ad-%s-%s' | format(type, banner.tile) %}
    <div>
        <script type="text/javascript" id="{{ scriptname }}">
            if (
                typeof AdController !== 'undefined'
                {% if type == 'desktop' and banner.tile == 2 -%}
                && window.Zeit.getClientWidth() > window.Zeit.sideAdMinWidth
                {% endif -%}
                && {{ operator | safe }}window.Zeit.isMobileView()
                ) {
                if( ! document.getElementById( "iqadtile{{ banner.tile }}" ) ) {
                    var elem = document.createElement('div');
                    elem.id = "iqadtile{{ banner.tile }}";
                    elem.className = "ad ad-{{ type }} ad-{{type}}--{{ banner.tile }} ad-{{type}}--{{ banner.tile }}-on-{{ pagetype }}";
                    elem.setAttribute('data-banner-type', '{{ type }}');
                    {% if banner.label and not(mobile) -%}
                        elem.setAttribute('data-banner-label', '{{ banner.label | lower }}');
                    {% endif -%}
                    document.getElementById('{{ scriptname }}').parentNode.appendChild(elem);
                    AdController.render('iqadtile{{ banner.tile }}');
                    if (window.console && typeof window.console.info === 'function') {
                        window.console.info('AdController ' + AdController.VERSION + ' tile {{ banner.tile }} {{ type }}')
                    }
                }
            }
        </script>
    </div>
  {% endif %}
{% endmacro %}

{% macro use_svg_icon(name, className, package, cleanup=True, a11y=True) -%}
    {#
        Generates in SVG, from minified svg file on disk, cleaned and a11y'd
        :param name: name of the svg file, w/o extension
        :param className: additional class to 'svg-symbol' (which is standard)
        :param package: the actual zeit.package i.e. zeit.web.site
        :param cleanup: clean svg from fill-attributes
        :param a11y: activate aria-label to read out svg/title/text()
    #}
    {# workaround for wrong packages comment icons #}
    {% set package = 'zeit.web.site' if 'zeit.web.core' == package else package %}
    {{ get_svg_from_file(name, className, package, cleanup, a11y) | safe }}
{%- endmacro %}

{% macro insert_esi(src, error_text='') %}
    {% if settings('use_wesgi') %}
        <!-- [esi-debug] src="{{ src | safe }}" error_text="{{ error_text }}" -->
        <esi:include src="{{ src | safe }}" onerror="continue" />
    {% else %}
        <esi:remove>
        <!-- [esi-debug] src="{{ src | safe }}" error_text="{{ error_text }}" -->
        </esi:remove>
        <!--esi
        <esi:include src="{{ src | safe }}" />
        -->
    {% endif %}
{% endmacro %}

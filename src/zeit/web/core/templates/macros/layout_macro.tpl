{% macro use_svg_icon(name, className, package, cleanup=True, a11y=True, remove_title=False) -%}
    {#
        Generates in SVG, from minified svg file on disk, cleaned and a11y'd
        :param name: name of the svg file, w/o extension
        :param className: additional class to 'svg-symbol' (which is standard)
        :param package: the actual zeit.package i.e. zeit.web.site
        :param cleanup: clean svg from fill-attributes
        :param a11y: activate aria-label to read out svg/title/text()
        :param remove_title: remove title-tag (so the tooltipp/hover shows the
            surrounding link-title ("Podcast bei Spotify") instead of svg-title ("Spotfy"))
    #}
    {# workaround for wrong packages comment icons #}
    {% set package = 'zeit.web.site' if 'zeit.web.core' == package else package %}
    {{ get_svg_from_file(name, className, package, cleanup, a11y, remove_title) | safe }}
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

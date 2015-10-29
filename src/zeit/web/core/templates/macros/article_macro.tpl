{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %} <!-- sinnvoll? -->

{% macro inlinegallery(obj, view=None, wrapper_class='inline-gallery__wrap') -%}
    <div class="{{ wrapper_class }}">
        <div class="inline-gallery">
            {% for entry in obj.itervalues() -%}
                {{ image(entry, loop) }}
            {%- endfor %}
        </div>
        <script type="text/template" class="inline-gallery-icon-templates">
        {% if view and not provides(view, 'zeit.magazin.interfaces.IZMOContent') %}
            <div class="bx-zone-prev">
                <a class="bx-overlay-prev">{{ lama.use_svg_icon('arrow-gallery-left', 'bx-arrow-icon', view.request) }}</a>
            </div>
            <div class="bx-zone-next">
                <a class="bx-overlay-next">{{ lama.use_svg_icon('arrow-gallery-right', 'bx-arrow-icon', view.request) }}</a>
            </div>
        {% else %}
            {# Needed by ZMO which still uses grunticon #}
            <div class="bx-zone-prev">
                <a class="bx-overlay-prev icon-pfeil-links"></a>
            </div>
            <div class="bx-zone-next">
                <a class="bx-overlay-next icon-pfeil-rechts"></a>
            </div>
        {% endif %}
        </script>
    </div>
{%- endmacro %}

{% macro no_block(obj) %}{% endmacro %}

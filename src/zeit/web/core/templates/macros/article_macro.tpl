{% macro inlinegallery(obj, wrapper_class='inline-gallery__wrap') -%}
    <div class="{{ wrapper_class }}">
        <div class="inline-gallery">
            {% for image in obj.itervalues() -%}
                {% set image_loop = loop %}
                {% include 'zeit.web.site:templates/inc/asset/image_gallery.tpl' with context %}
            {%- endfor %}
        </div>
    </div>
{%- endmacro %}

{% macro no_block(obj) %}{% endmacro %}

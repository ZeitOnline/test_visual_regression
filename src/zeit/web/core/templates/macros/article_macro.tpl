{% macro inlinegallery(obj, wrapper_class='inline-gallery__wrap') -%}
    <div class="{{ wrapper_class }}">
        <div class="inline-gallery">
            {% for entry in obj.itervalues() -%}
                {{ image(entry, loop) }}
            {%- endfor %}
        </div>
    </div>
{%- endmacro %}

{% macro no_block(obj) %}{% endmacro %}

{% import 'zeit.web.magazin:templates/macros/layout_macro.tpl' as lama with context %}

{% macro advertorial_modifier(product, is_advertorial) -%}
    {% if (product.title == 'Advertorial' and not is_advertorial) %} is-advertorial{% endif %}
{%- endmacro %}

{% macro headervideo_linked(obj, wrap_class='article__main-video--longform', img_class='', href='') -%}

    {% if obj.id is not defined and obj.uniqueId -%}
        {% set id = obj.uniqueId | substring_from('/') %}
    {% elif obj.id -%}
        {% set id = obj.id %}
    {% endif %}

    {% if id %}
        <div data-backgroundvideo="{{ id }}" class="{{ wrap_class }}">
            {% if href %}
            <a href="{{ href }}">
            {% endif %}
                <video preload="auto" loop="loop" muted="muted" volume="0" poster="{{ obj.video_still }}">
                    <source src="{{ obj.highest_rendition_url }}" type="video/mp4">
                    <source src="http://live0.zeit.de/multimedia/videos/{{ id }}.webm" type="video/webm">
                </video>
                <img class="video--fallback {{ img_class }}" src="http://live0.zeit.de/multimedia/videos/{{ id }}.jpg" alt="Video: {{ obj.title }}" title="Video: {{ obj.title }}">
            {% if href %}
            </a>
            {% endif %}
        </div>
    {% endif %}
{%- endmacro %}

{% import 'zeit.web.magazin:templates/macros/layout_macro.tpl' as lama with context %}

{% macro include_module(obj) -%}
    {% if obj -%}
        {% for module in obj -%}
            {% if module.layout -%}
                {{ include_teaser(module) }}
                {% if view.is_hp and loop.first and module.layout.id == 'zmo-square-large' %}
                    {{ lama.adplace(view.banner(3), view, True) }}
                {% endif %}
            {% endif %}
        {% endfor %}
    {% endif %}
{%- endmacro %}

{% macro include_module_with_ad(obj) -%}
    {% if obj -%}
        {% for module in obj -%}
            {% if module.layout -%}
                {{ include_teaser(module) }}

                {% if (loop.index == 2 or loop.last) and (added is not defined) -%}
                    <!-- special ad integration by counter -->
                    {% set added = true %}
                    {{ include_cp_ad() }}
                {% endif %}
            {% endif %}
        {% endfor %}
    {% endif %}
{%- endmacro %}

{% macro include_ad_tile_4(view) %}
    {{ lama.adplace(view.banner(4), view, True) }}
{% endmacro %}

{% macro include_teaser(module, prefix) -%}
    {% if prefix is not defined -%}
        {% set prefix = '' -%}
    {% endif %}
    {% if module is iterable -%}
        {% for teaser in module %}
            {% include ['zeit.web.magazin:templates/inc/teaser/' + prefix + module.layout.id + '.tpl',
            'zeit.web.magazin:templates/inc/teaser/default.tpl'] ignore missing %}
        {% endfor %}
    {% endif %}
{%- endmacro %}

{% macro include_cp_ad() -%}
    <div class="cp_button--ad">
        {% if view %}
            {{ lama.adplace(view.banner(7), view) }}
        {% endif %}
    </div>
{%- endmacro %}

{% macro teaser_sharing_card(teaser) -%}
    <div class="card__slider">
        <div class="card__slide js-slide-card">
            <div class="card__sharing-icons">
                <a href="http://twitter.com/home?status={{teaser | create_url | e}}"
                    class="card__sharing-icon js-stop-propagation icon-twitter" target="_blank" title="Auf Twitter teilen"></a>

                <a href="https://plus.google.com/share?url={{teaser | create_url | e}}"
                    class="card__sharing-icon js-stop-propagation icon-google" target="_blank" title="Auf Google+ teilen"></a>

                <a href="http://www.facebook.com/sharer/sharer.php?u={{teaser | create_url | e}}"
                    class="card__sharing-icon js-stop-propagation icon-facebook" target="_blank" title="Auf Facebook teilen"></a>

                <a href="mailto:?subject={{teaser.teaserTitle}}&amp;body={{teaser | create_url | e}}" class="card__sharing-icon js-stop-propagation icon-mail" title="Per Mail senden"></a>
            </div>
        </div>
    </div>
{%- endmacro %}


{% macro advertorial_modifier(product_text, is_advertorial) -%}
    {% if (product_text == 'Advertorial' and not is_advertorial) %} is-advertorial{% endif %}
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
                    <source src="{{ obj.highest_rendition }}" type="video/mp4">
                    <source src="http://live0.zeit.de/multimedia/videos/{{ id }}.webm" type="video/webm">
                </video>
                <img class="video--fallback {{ img_class }}" src="http://live0.zeit.de/multimedia/videos/{{ id }}.jpg" alt="Video: {{ obj.title }}" title="Video: {{ obj.title }}">
            {% if href %}
            </a>
            {% endif %}
        </div>
    {% endif %}
{%- endmacro %}

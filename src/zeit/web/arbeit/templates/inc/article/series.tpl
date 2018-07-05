{% if view.has_series_attached %}
    {% set series_cp = context | find_series_cp %}
    {% set image = get_image(series_cp, variant_id='stripe', fallback=False) %}

    <div class="{{ 'article-series' | with_mods('has-image' if image) }}" data-ct-area="articleheader" data-ct-row="series" data-ct-column="false">
        {% if image -%}
            {% set module_layout = "article-series" %}
            {% set media_caption_additional_class = 'figcaption--hidden' %}
            {% set media_block_additional_class = 'is-pixelperfect' -%}
            {% include "zeit.web.core:templates/inc/asset/image.tpl" %}
        {%- endif -%}

        <a href="{{ series_cp | create_url }}" class="article-series__heading" data-ct-label="{{ view.serie }}">
            <span class="article-series__title">Aus der Serie: {{ view.serie }}</span>
        </a>
    </div>
{% endif %}

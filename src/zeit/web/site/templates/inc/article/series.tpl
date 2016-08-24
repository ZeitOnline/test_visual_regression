{% if view.has_series_attached %}
    <div class="article-series">
        {% require image = get_image(view, view.series, variant_id='stripe', fallback=False) -%}
            {% set module_layout = "article-series" %}
            {% set media_caption_additional_class = 'figcaption--hidden' %}
            {% set media_block_additional_class = 'is-pixelperfect' -%}
            {% include "zeit.web.core:templates/inc/asset/image.tpl" %}
        {%- endrequire -%}

        <a href="{{ view.series | create_url }}" class="article-series__heading" itemprop="isPartOf">
            <div class="article-series__inner-heading">
                <span class="article-series__kicker">Aus der Serie</span><span class="visually-hidden">: </span>
                <span class="article-series__title">{{ view.serie }}</span>
            </div>
        </a>
    </div>
{% endif %}

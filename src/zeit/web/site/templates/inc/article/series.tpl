{% if view.has_series_attached %}
    <div class="article-series" data-ct-row="series" data-ct-column="false">
        {% set series_cp = context | find_series_cp %}
        {% require image = get_image(series_cp, variant_id='stripe', fallback=False) -%}
            {% set module_layout = "article-series" %}
            {% set media_caption_additional_class = 'figcaption--hidden' %}
            {% set media_block_additional_class = 'is-pixelperfect' -%}
            {% include "zeit.web.core:templates/inc/asset/image.tpl" %}
        {%- endrequire -%}

        <a href="{{ series_cp | create_url }}" class="article-series__heading" data-ct-label="{{ view.serie }}">
            <div class="article-series__inner-heading">
                <span class="article-series__kicker">Aus der Serie</span><span class="visually-hidden">: </span>
                <span class="article-series__title">{{ view.serie }}</span>
            </div>
        </a>
    </div>
{% endif %}

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
<div class="article__item">
    {% set headertag = 'div' if view.pagination and view.pagination.current > 1 and view.current_page.teaser else 'h1' %}
    <{{ headertag }} class="article-heading" itemprop="headline">
        <span class="article-heading__kicker">
            {%- if view.context is column -%}
                {{- view.serie + ' / ' -}}
            {%- endif -%}
            {{- view.supertitle -}}
        </span>
        {%- if view.title %}<span class="visually-hidden">: </span>{% endif -%}
        <span class="article-heading__title">
            {{- view.title -}}
        </span>
    </{{ headertag }}>
</div>

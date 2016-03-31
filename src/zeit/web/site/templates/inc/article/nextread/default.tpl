{% set image = get_image(module, teaser, fallback=False) %}
{% set comments = view.comment_counts.get(teaser.uniqueId, 0) %}
{% set module_layout = self.layout() %}
{% set modifier = '--with-image' if image and not is_image_expired(image) else '--no-image' %}
<article id="{{ module_layout }}"
         class="{% block layout %}nextread{% endblock %} {{ module_layout }}{{ modifier }}">
    <a class="{{ module_layout }}__link" title="{{ teaser.supertitle }}: {{ teaser.title }}" href="{{ teaser.uniqueId | create_url }}" data-id="articlebottom.editorial-nextread...area" itemprop="relatedLink">
        <div class="{{ module_layout }}__lead">{{ module.lead or 'Lesen Sie jetzt' }}</div>
        {% include "zeit.web.core:templates/inc/asset/image_nextread.tpl" %}
        <div class="{{ module_layout }}__container">
            <h2 class="{{ module_layout }}__heading">
                <span class="{{ module_layout }}__kicker">{{ teaser.teaserSupertitle or teaser.supertitle }}</span>
                {%- if teaser.teaserTitle or teaser.title %}<span class="visually-hidden">: </span>{% endif -%}
                <span class="{{ module_layout }}__title">{{ teaser.teaserTitle or teaser.title }}</span>
            </h2>
            <div class="{{ module_layout }}__metadata">
                {% set byline = teaser | get_byline %}
                {% if byline | length %}
                <span class="{{ module_layout }}__byline">
                    {%- include 'zeit.web.core:templates/inc/meta/byline.html' -%}
                </span>
                {% endif %}
                {{ cp.include_teaser_datetime(teaser, module_layout, module_layout) }}
                {% if comments %}
                    <span class="{{ module_layout }}__commentcount">
                        {{ comments | pluralize('Keine Kommentare', '{} Kommentar', '{} Kommentare') }}
                    </span>
                {% endif %}
            </div>
        </div>
    </a>
</article>

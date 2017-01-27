{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}

{% set image = get_image(module, fallback=False) %}
{% set comments = view.comment_counts.get(teaser.uniqueId, 0) %}
{% set module_layout = self.layout() %}
{% if teaser is zplus_content %}
    {% set data_id = "articlebottom.editorial-nextread...area-zplus" %}
{% else %}
    {% set data_id = "articlebottom.editorial-nextread...area" %}
{% endif %}

<article id="{{ module_layout }}"
         class="{% block layout %}nextread{% endblock %} {{ module_layout }}{{ '--with-image' if (image and teaser is not column) else '--no-image' }}">
    <a class="{{ module_layout }}__link" title="{{ teaser.supertitle }}: {{ teaser.title }}" href="{{ teaser.uniqueId | create_url }}" data-id={{ data_id }} itemprop="relatedLink">
        <div class="{{ module_layout }}__lead">{{ module.lead or 'Lesen Sie jetzt' }}</div>
        {% if teaser is not column %}
            {% include "zeit.web.core:templates/inc/asset/image_nextread.tpl" %}
        {% endif %}
        <div class="{{ module_layout }}__container">
            <h2 class="{{ module_layout }}__heading">
                <span class="{{ module_layout }}__kicker">
                {% if teaser is zplus_content %}
                    {{ lama.use_svg_icon('zplus', module_layout + '__kicker-logo--zplus svg-symbol--hide-ie', view.package, a11y=False) }}
                {% elif tag_with_logo_content %}
                    {{ lama.use_svg_icon(tag_with_logo_content, self.layout() + '__kicker-logo--tag svg-symbol--hide-ie', 'zeit.web.site', a11y=False) }}
                {% endif %}
                {{ teaser.teaserSupertitle or teaser.supertitle }}
                </span>
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
                {% if comments and teaser.commentSectionEnable %}
                    <span class="{{ module_layout }}__commentcount">
                        {{ comments | pluralize('Keine Kommentare', '{} Kommentar', '{} Kommentare') }}
                    </span>
                {% endif %}
            </div>
        </div>
    </a>
</article>

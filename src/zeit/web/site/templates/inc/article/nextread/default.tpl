{% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama %}

{% set image = get_image(module, fallback=False) %}
{% set comments = view.comment_counts.get(teaser.uniqueId, 0) %}
{% set module_layout = self.layout() %}
{% if teaser is zplus_abo_content %}
    {% set data_id = "articlebottom.editorial-nextread...area-zplus" %}
{% elif teaser is zplus_registration_content %}
    {% set data_id = "articlebottom.editorial-nextread...area-zplus-register" %}
{% else %}
    {% set data_id = "articlebottom.editorial-nextread...area" %}
{% endif %}

<article id="{{ module_layout }}"
         class="{% block layout %}nextread{% endblock %} {{ module_layout }}{{ '--with-image' if (image and teaser is not column) else '--no-image' }}">
    <a class="{{ module_layout }}__link" title="{{ teaser.supertitle }}: {{ teaser.title }}" href="{{ teaser.uniqueId | create_url }}" data-id="{{ data_id }}">
        <div class="{{ module_layout }}__lead">{{ module.lead or 'Lesen Sie jetzt' }}</div>
        {% if teaser is not column %}
            {% include "zeit.web.core:templates/inc/asset/image_nextread.tpl" %}
        {% endif %}
        <div class="{{ module_layout }}__container">
            <h2 class="{{ module_layout }}__heading">
                <span class="{{ '%s__kicker' | format(module_layout) | with_mods(teaser | branding) }}">
                {% set logo_layout = self.layout() %}
                {% for template in teaser | logo_icon() %}
                    {% include "zeit.web.core:templates/inc/badges/{}.tpl".format(template) %}
                {% endfor %}
                {{ teaser.teaserSupertitle or teaser.supertitle -}}
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

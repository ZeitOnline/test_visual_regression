{% set image = get_image(module, teaser, fallback=False) %}
{% set comments = view.comment_counts.get(teaser.uniqueId, 0) %}
{% set module_layout = self.layout() %}

<article class="{% block layout %}nextread{% endblock %}{% if not image %} {{ module_layout }}--no-image{% else %} {{ module_layout }}--with-image{% endif %}" id="{{ module_layout }}">
    <a class="{{ module_layout }}__link" title="{{ teaser.supertitle }}: {{ teaser.title }}" href="{{ teaser.uniqueId | create_url }}" data-id="articlebottom.editorial-nextread...area">
        <div class="{{ module_layout }}__lead">{{ module.lead or 'Lesen Sie jetzt' }}</div>
        {% include "zeit.web.site:templates/inc/asset/image_nextread-default.tpl" with context %}
        <div class="{{ module_layout }}__container">
            <h2 class="{{ module_layout }}__heading">
                <span class="{{ module_layout }}__kicker">{{ teaser.teaserSupertitle or teaser.supertitle }}</span>
                <span class="{{ module_layout }}__title">{{ teaser.teaserTitle or teaser.title }}</span>
            </h2>
            <div class="{{ module_layout }}__metadata">
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

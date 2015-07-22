{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}
{% import 'zeit.web.site:templates/macros/centerpage_macro.tpl' as cp %}

{% block teaser %}

<article class="{% block layout %}{{ layout | default('default') }}{% endblock %} {% block teaser_modifier %}{% endblock %}"{% if module %} data-block-type="{{ module.type | hide_none }}"{% endif %} data-unique-id="{{ teaser.uniqueId }}" data-meetrics="{{ area.kind }}">

    {% block teaser_media_position_before_title %}{% endblock %}

    <div class="{{ self.layout() }}__container {% block teaser_container_modifier %}{% endblock %}">

        {% block teaser_journalistic_format %}
            {% if teaser.serie and not teaser.serie.column %}
                <div class="{{ self.layout() }}__series-label">Serie: {{ teaser.serie.serienname }}</div>
            {% endif %}
        {% endblock teaser_journalistic_format%}

        <h2 class="{{ self.layout() }}__heading {% block teaser_heading_modifier %}{% endblock %}">
            {% block teaser_link %}
            <a class="{{ self.layout() }}__combined-link" title="{{ teaser.teaserSupertitle or teaser.supertitle | hide_none }} - {{ teaser.teaserTitle or teaser.title | hide_none }}" href="{{ teaser.uniqueId | create_url }}">
                {% block teaser_kicker %}
                <span class="{{ self.layout() }}__kicker">{{ teaser.teaserSupertitle or teaser.supertitle | hide_none }}</span>
                {% endblock %}
                {% block teaser_title %}
                <span class="{{ self.layout() }}__title">{{ teaser.teaserTitle or teaser.title | hide_none }}</span>
                {% endblock %}
                {% block teaser_product %}
                   {# Use this for short teaser #}
                {% endblock %}
            </a>
            {% endblock %}
        </h2>

        {% block teaser_media_position_after_title %}{% endblock %}

        {% block teaser_container %}
            {% block teaser_text %}
                {# TODO: Extract teaser-length text snippet from articles that don't have a teaser text. #}
                <p class="{{ self.layout() }}__text">{{ teaser.teaserText | hide_none }}{% block teaser_byline_inner %}{% endblock %}</p>
            {% endblock %}
            {% block teaser_byline %}
                <span class="{{ self.layout() }}__byline">
                    {% set byline = teaser | get_byline %}
                    {% include 'zeit.web.site:templates/inc/meta/byline.tpl' %}
                </span>
            {% endblock %}
            {% block teaser_metadata_default %}
            <div class="{{ self.layout() }}__metadata">
                {% block teaser_datetime %}
                    {{ cp.include_teaser_datetime(teaser, self.layout()) }}
                {% endblock %}
                {% block teaser_commentcount %}
                    {% set comments = view.comment_counts[teaser.uniqueId] %}
                    {% if comments %}
                        {% set comments_string = comments | pluralize('Keine Kommentare', '{} Kommentar', '{} Kommentare') %}
                        <a class="{{ self.layout() }}__commentcount js-update-commentcount" href="{{ teaser.uniqueId | create_url }}#comments" title="Kommentare anzeigen">{{ comments_string }}</a>
                    {% endif %}
                {% endblock %}
            </div>
            {% endblock %}
        {% endblock %}
    </div>

    {% block teaser_media_position_after_container %}{% endblock %}

</article>
{% endblock %}

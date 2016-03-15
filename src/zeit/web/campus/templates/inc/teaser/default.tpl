<article class="{% block layout %}{{ layout | default('default') }}{% endblock %} {% block teaser_modifier %}{% endblock %}{% if module.visible_mobile == False %} mobile-hidden{% endif %}"
    data-unique-id="{{ teaser.uniqueId }}"
    {% block meetrics %} data-meetrics="{{ area.kind }}"{% endblock %}
    data-clicktracking="{{ area.kind }}"
    {% block teaser_attributes %}{% endblock %}>

    {% block teaser_media %}{% endblock %}

    {% block teaser_content %}
        {% block teaser_heading %}
            <h2 class="{{ self.layout() }}__heading {% block teaser_heading_modifier %}{% endblock %}">
                {% block teaser_link %}
                <a class="{{ self.layout() }}__combined-link"
                   title="{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}"
                   href="{{ teaser | create_url | append_campaign_params }}">
                    {% block teaser_kicker %}
                        <span class="{{ self.layout() }}__kicker">
                            {{ teaser.teaserSupertitle or teaser.supertitle -}}
                        </span>
                        {%- if teaser.teaserSupertitle or teaser.supertitle -%}
                            <span class="visually-hidden">: </span>
                        {% endif %}
                    {% endblock %}
                    {% block teaser_title %}
                        <span class="{{ self.layout() }}__title">{{ teaser.teaserTitle or teaser.title }}</span>
                    {% endblock %}
                    {% block teaser_product %}
                       {# Use this for short teaser #}
                    {% endblock %}
                </a>
                {% endblock teaser_link %}
            </h2>
        {% endblock teaser_heading %}
        {% block teaser_text %}
            <p class="{{ self.layout() }}__text">{{ teaser.teaserText }}</p>
        {% endblock teaser_text %}

        {% block teaser_metadata_default %}
        <div class="{{ self.layout() }}__metadata">
            {% block teaser_byline %}
                {% set byline = teaser | get_byline %}
                {% if byline | length %}
                <span class="{{ self.layout() }}__byline">
                    {%- include 'zeit.web.site:templates/inc/meta/byline.tpl' -%}
                </span>
                {% endif %}
            {% endblock teaser_byline %}
            {% block teaser_datetime %}
                {# disable for now, til macro is ported 
					{% if not view.is_advertorial %}
                    {{ cp.include_teaser_datetime(teaser, self.layout(), area.kind) }}
	                {% endif %}
				#}
            {% endblock teaser_datetime %}
            {% block teaser_commentcount %}
                {% set comments = view.comment_counts[teaser.uniqueId] %}
                {% if comments %}
                    {% set comments_string = comments | pluralize('Keine Kommentare', '{} Kommentar', '{} Kommentare') %}
                    <a class="{{ self.layout() }}__commentcount js-update-commentcount" href="{{ teaser | create_url }}#comments" title="Kommentare anzeigen">{{ comments_string }}</a>
                {% endif %}
            {% endblock teaser_commentcount %}
        </div>
        {% endblock teaser_metadata_default %}

    {% endblock teaser_content %}
</article>

{%- extends "zeit.web.arbeit:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-quote{% endblock %}

{# The quote teaser has another order of content (text, heading, image) than default #}

{% block teaser_allcontent %}
    {% block teaser_text %}
        <a class="{% block quotelink_class %}{{ self.layout() }}__quotelink{% endblock %}"
                   title="{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}"
                   href="{{ teaser | create_url | append_campaign_params }}">
            <p class="{{ self.layout() }}__text">
                {% set citation = get_first_citation(teaser.uniqueId) %}
                {% if citation %}
                    {{- citation.text -}}
                {% else %}
                    {{- teaser.teaserText -}}
                {% endif %}
            </p>
        </a>{% endblock %}

    <div class="{{ self.layout() }}__headingwrapper">
        {% block teaser_heading %}{{ super() }}{% endblock %}
        {% block teaser_byline %}{{ super() }}{% endblock %}
    </div>

    {% block teaser_media %}
        {% if teaser is column %}
            {% set module_layout = self.layout() %}
            {% include "zeit.web.arbeit:templates/inc/teaser/asset/image_teaser_zar-quote-column.tpl" %}
        {% endif %}
    {% endblock %}
{% endblock %}

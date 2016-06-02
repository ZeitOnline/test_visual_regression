{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-author{% endblock %}

{% block teaser_media_position_before_title %}
    <a href="{{ teaser | create_url }}" class="{{ self.layout() }}__overall-link" title="{{ teaser.display_name }}">
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/asset/image_zon-author.tpl" %}
    <div class="{{ self.layout() }}__overlay"></div>
{% endblock %}

{% block teaser_heading %}
    <h2 class="{{ self.layout() }}__heading">{{ teaser.display_name }}</h2>
{% endblock %}

{% block teaser_container %}
    <p class="{{ self.layout() }}__text">{{ teaser.summary }}</p>
    <button class="{{ self.layout() }}__button">Zum Profil</button>
{% endblock %}

{% block teaser_media_position_after_container %}
    </a>
{% endblock %}

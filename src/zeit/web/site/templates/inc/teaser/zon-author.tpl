{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-author{% endblock %}

{% block teaser_media_position_before_title %}
	{% include "zeit.web.site:templates/inc/asset/image_zon-author.tpl" %}
{% endblock %}

{% block media_caption_content %}{% endblock %}

{% block teaser_kicker %}{% endblock %}

{% block teaser_title %}
	<span class="{{ self.layout() }}__title">{{ teaser.display_name }}</span>
{% endblock %}

{% block teaser_text %}
	<span class="{{ self.layout() }}__text">Wartet auf ZON-2657</span>
	<a href="{{ teaser | create_url }}" class="{{ self.layout() }}__button">Zum Profil</a>
{% endblock %}

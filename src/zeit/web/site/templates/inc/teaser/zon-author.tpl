{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-author{% endblock %}

{% block teaser_media_position_before_title %}
    {% include "zeit.web.site:templates/inc/asset/image_zon-author.tpl" %}
{% endblock %}

{% block media_caption_content %}{% endblock %}

{% block teaser_kicker %}
    {{ teaser.display_name }}
{% endblock %}

{% block teaser_text %}
    Wartet auf ZON-2657
{% endblock %}

{% block teaser_media_position_after_container %}
	<a href="{{ teaser | create_url }}" class="{{ self.layout() }}__button">Zum Profil</a>
{% endblock %}

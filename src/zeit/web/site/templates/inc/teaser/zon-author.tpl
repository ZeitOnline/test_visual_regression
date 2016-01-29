{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-author{% endblock %}

{% block teaser_media_position_before_title %}
    {% include "zeit.web.site:templates/inc/asset/image_zon-author.tpl" %}
{% endblock %}

{% block media_caption_content %}{% endblock %}

{% block teaser_kicker %}
    {{ teaser.display_name }}
{% endblock %}

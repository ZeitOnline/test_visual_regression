{%- extends "zeit.web.site:templates/inc/videostage/abstract-video.tpl" -%}

{% block layout %}video-small{% endblock %}

{% block playbutton_modifier %}inline{% endblock %}

{% block playbutton %}{% endblock %}

{% block video_thumbnail %}
    {% set image = (video | get_image_group)['still.jpg'] %}
    {% include "zeit.web.site:templates/inc/teaser_asset/image_videostage_small.tpl" %}
{% endblock video_thumbnail %}
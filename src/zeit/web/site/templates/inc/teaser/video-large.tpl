{%- extends "zeit.web.site:templates/inc/teaser/abstract-video.tpl" -%}

{% block layout %}video-large{% endblock %}

{% block meetrics %}{{ area.kind }}{% endblock %}

{% block playbutton_modifier %}block{% endblock %}

{% block description %}<p class="{{ self.layout() }}__description">{{ teaser.teaserText }}</p>{% endblock %}

{% block inlineplaybutton %}{% endblock %}

{% block data_video_size %} data-video-size="large"{% endblock %}

{%- extends "zeit.web.site:templates/inc/teaser/abstract-video.tpl" -%}

{% block layout %}video-large{% endblock %}

{% block description %}<p class="{{ self.layout() }}__description">{{ teaser.teaserText }}</p>{% endblock %}

{% block byline %}
    {%- set byline = teaser | get_byline %}
    {% if byline | length -%}
        <div class="{{ self.layout() ~ '__byline' }}">
            {% include 'zeit.web.core:templates/inc/meta/byline.html' %}
        </div>
    {% endif %}
{% endblock %}

{% block inlineplaybutton %}{% endblock %}

{% block data_video_size %} data-video-size="large"{% endblock %}


{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-large{% endblock %}

{% block teaser_media_position_after_title %}
    {% set module_layout = self.layout() %}
    {% if teaser | is_video %}
		{% set media_container_additional_class = 'teaser-media-container--has-icon' %}
		{% set media_container_after = lama.use_svg_icon('video', 'teaser-image-icon teaser-image-icon--on-{}'.format(module_layout), view.package) %}
	{% endif %}
    {% include "zeit.web.core:templates/inc/asset/image_teaser.tpl" ignore missing %}
{% endblock %}

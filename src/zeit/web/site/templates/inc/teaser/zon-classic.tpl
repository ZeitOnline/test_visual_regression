{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-classic{% endblock %}

{% block teaser_media_position_after_title %}
    {% set module_layout = self.layout() %}
    {% if teaser | is_video %}
		{% set media_container_additional_class = 'teaser-media-container--has-icon' %}
		{% set media_container_after = lama.use_svg_icon('video', 'teaser-image-icon teaser-image-icon--on-{}'.format(module_layout), request) %}
	{% endif %}
    {% include "zeit.web.site:templates/inc/teaser_asset/{}_zon-fullwidth.tpl".format(teaser | auto_select_asset | block_type) ignore missing %}
{% endblock %}

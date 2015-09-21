{%- extends "zeit.web.site:templates/inc/teaser/zon-small.tpl" -%}

{% block layout %}teaser-small-minor{% endblock %}

{% if module.force_mobile_image %}
	{% set media_block_additional_class = 'teaser-small-minor__media--force-mobile' %}
{% endif %}	

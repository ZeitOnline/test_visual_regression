{#
Teaser template for gallery upright teaser
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-upright{% endblock %}
{% block icon %}
	{% if teaser | is_gallery -%}
		{{ lama.use_svg_icon('gallery', '%s__gallery-icon' | format(self.layout()), request) }}
	{%- endif %}
{% endblock %}
{% block teaser_text %}{% endblock %}

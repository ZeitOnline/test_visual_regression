{#
Teaser template for gallery upright teaser
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-upright{% endblock %}
{% block icon %}
	{% if teaser | is_gallery %}
	    <span class="icon-galerie-icon-white"></span>
	{% endif %}
{% endblock %}
{% block teaser_text %}{% endblock %}

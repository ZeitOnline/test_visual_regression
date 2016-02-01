{#

Teaser template for mtb square button teaser

Parameters:
    subtitle: to define display of subtitle
    format: to define type of button
    supertitle: to define display of supertitle
    icon: define display of optional asset icon
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/default.tpl" -%}

{% block teaser_text %}{% endblock %}
{% block format %}mtb{% endblock %}
{# block image_class %}mtb__teaser__image{% endblock }
	TODO AS: fix it… this was the only teaser that used a separate image_class, like so:
	<div class="scaled-image is-pixelperfect cp_button__image">
	    {{ lama.insert_responsive_image(image) }}
	{%- endif %}
#}

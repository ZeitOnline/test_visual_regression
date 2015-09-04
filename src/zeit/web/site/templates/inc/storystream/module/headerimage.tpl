{% set blockname = 'storystream-headerimage' %}
<header class="{{ blockname }}">
    {# get the image directy from the supplied image group #}
    {% set image = get_image(module, default='panorama') %}
    {# we need to explecitly pass the layout aka block class name #}
    {% set module_layout = "header-image" %}
    {% include "zeit.web.site:templates/inc/module/headerimage_image.tpl" ignore missing %}

	<div class="{{ blockname }}__container">
    	<span class="{{ blockname }}__kicker">{{ view.supertitle }}</span>
    	<h1 class="{{ blockname }}__title">{{ view.title }}</h1>
    </div>
</header>

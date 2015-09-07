{% set blockname = 'storystream-headerimage' %}
<header class="{{ blockname }}">
    {# get the image directy from the supplied image group #}
    {% set image = get_image(module, default='panorama') %}
    {# we need to explecitly pass the layout aka block class name #}
    {% set module_layout = "header-image" %}
    {% include "zeit.web.site:templates/inc/module/headerimage_image.tpl" ignore missing %}

	<div class="{{ blockname }}__container">
    	<span class="{{ blockname }}__kicker">{{ view.context.supertitle }}</span>
    	<h1 class="{{ blockname }}__title">{{ view.context.title }}</h1>
    	<span class="{{ blockname }}__update">Zuletzt aktualisiert am 9. Juni 2015</span>
    </div>
</header>

{% include 'zeit.web.site:templates/inc/storystream/meta/sharing.tpl' %}

<div class="storystream-summary">
    <p  itemprop="description">{{ view.context.subtitle }}</p>
    <p itemscope itemtype="http://schema.org/Person" itemprop="author">
        {% set byline = view.context | get_byline %}
        {% include 'zeit.web.site:templates/inc/meta/byline.tpl' %}
    </p>
</div>

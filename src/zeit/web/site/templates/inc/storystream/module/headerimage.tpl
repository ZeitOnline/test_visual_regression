{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}

{% set blockname = 'storystream-headerimage' %}
<header class="{{ blockname }}">
    {# get the image directy from the supplied image group #}
    {% set image = get_image(module, default='cinema') %}
    {# we need to explecitly pass the layout aka block class name #}
    {% set module_layout = blockname %}
    {% include "zeit.web.site:templates/inc/storystream/inc/headerimage_image.tpl" ignore missing %}

    <div class="{{ blockname }}__wrapper">
        <div class="{{ blockname }}__container">
        	<div class="{{ blockname }}__content">
            	<span class="{{ blockname }}__kicker">{{ module.supertitle }}</span>
            	<h1 class="{{ blockname }}__title">{{ module.title }}</h1>
                {% if view.date_last_modified %}
                	<span class="{{ blockname }}__update">
                        {{ lama.use_svg_icon('storystream-updated', 'storystream-headerimage__updateicon', request) }}
                        Zuletzt aktualisiert am <nobr>{{ view.date_last_modified | format_date('short') }}</nobr>
                    </span>
                {% endif %}
            </div>
        </div>
    </div>
</header>

{% include 'zeit.web.site:templates/inc/storystream/meta/sharing.tpl' %}
{% include 'zeit.web.site:templates/inc/storystream/meta/summary.tpl' %}

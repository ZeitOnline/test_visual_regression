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
            	<span class="{{ blockname }}__kicker">
                    <span class="{{ blockname }}__kicker-label">Live-Dossier</span>
                    <span class="{{ blockname }}__kicker-text">{{ module.supertitle }}</span>
                </span>
            	<h1 class="{{ blockname }}__title" itemprop="headline">{{ module.title }}</h1>
                <time itemprop="datePublished" datetime="{{ view.date_first_released | format_date('iso8601') }}"></time>
                {% if view.date_last_modified %}
                	<span class="{{ blockname }}__update">
                        {{ lama.use_svg_icon('storystream-updated', 'storystream-headerimage__updateicon', view.package) }}
                        Zuletzt aktualisiert am
                        <time class="{{ blockname }}__date" itemprop="dateModified" datetime="{{ view.date_last_modified | format_date('iso8601') }}">
                            {{- view.date_last_modified | format_date('short') -}}
                        </time>
                    </span>
                {% endif %}
            </div>
        </div>
    </div>
</header>

{% include 'zeit.web.site:templates/inc/storystream/meta/sharing.tpl' %}
{% include 'zeit.web.site:templates/inc/storystream/meta/summary.tpl' %}

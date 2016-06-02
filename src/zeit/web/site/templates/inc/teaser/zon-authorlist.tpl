<li class="author-list__item">
    {% set module_layout = 'zon-author-list' %}
    {% if get_image(content=teaser, variant_id='original', fallback=False, fill_color=None) %}
        <a href="{{ teaser | create_url }}">
            <div class="{{ module_layout }}__imageitem">
                <div class="{{ module_layout }}__image">
                    {% include "zeit.web.site:templates/inc/asset/image_zon-author-list.tpl" ignore missing %}
                </div>
                <div class="{{ module_layout }}__text">
                    <h3 class="{{ '{}__name'.format(module_layout) | with_mods('without-summary' if not teaser.summary) }}">{{ teaser.display_name }}</h3>
                    {% if teaser.summary -%}
                        <p class="{{ module_layout }}__summary">{{ teaser.summary }}</p>
                    {%- endif %}
                </div>
            </div>
        </a>
    {% else %}
        <span class="{{ module_layout }}__textitem">
            <a class="{{ module_layout }}__textitem-link" href="{{ teaser | create_url }}">{{ teaser.display_name }}</a>
        </span>
    {% endif %}
</li>

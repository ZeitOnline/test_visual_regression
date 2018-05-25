<li class="author-list__item">
    {% set module_layout = 'zon-author-list' %}
    {% set image = get_image(teaser, variant_id='square', fallback=False) %}
    {% if image %}
        <a href="{{ teaser | create_url }}">
            <div class="{{ module_layout }}__imageitem">
                {% include "zeit.web.site:templates/inc/asset/image_zon-author-list.tpl" %}
                <div class="{{ module_layout }}__text">
                    <h3 class="{{ '{}__name'.format(module_layout) | with_mods('without-summary' if not teaser.summary) }}">{{ teaser.display_name }}</h3>
                    {% if teaser.summary -%}
                        <p class="{{ module_layout }}__summary">{{ teaser.summary }}</p>
                    {%- endif %}
                </div>
            </div>
        </a>
    {% else %}
        <a class="{{ module_layout }}__textitem" href="{{ teaser | create_url }}">{{ teaser.display_name | trim }}</a>
    {% endif %}
</li>

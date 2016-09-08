<div class="zplus">
    <div class="zplus__badge article__item article__item--rimless">
        {%  if view.context.acquisition == 'abo' %}
            <div class="zplus__marker">
                {{ lama.use_svg_icon('zplus', 'zplus__marker-icon svg-symbol--hide-ie', view.package, a11y=False) }}
            </div>
        {% endif %}
        <div class="zplus__label">
            {% if view.zplus_label %}
                <div class="zplus__label-intro">{{ view.zplus_label.intro }}</div>
                <a class="zplus__label-link" href="{{ view.zplus_label.link }}">
                    {{ view.zplus_label.link_text }}
                </a>
            {% endif %}
        </div>
        {% set image = get_image(view.zplus_label.cover) %}
        {% include "zeit.web.core:templates/inc/asset/image_linked.tpl" ignore missing %}
    </div>
</div>

<div class="zplus">
    <div class="zplus__badge article__item article__item--rimless">
        {%  if view.context.acquisition == 'abo' %}
            <div class="zplus__marker">
                {{ lama.use_svg_icon('zplus', 'zplus__marker-icon svg-symbol--hide-ie', view.package, a11y=False) }}
            </div>
        {% endif %}
        <div class="zplus__text">
            {% if view.zplus_label %}
                <span class="zplus__label">{{ view.zplus_label.intro }}</span>
                <a class="zplus__link" href="{{ view.zplus_label.link }}">
                    {{ view.zplus_label.link_text }}
                </a>
            {% endif %}
        </div>
        {% if view.zplus_label.cover %}
            {% include "zeit.web.core:templates/inc/asset/image_cover.tpl" ignore missing %}
        {% endif %}
    </div>
</div>

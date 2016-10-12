{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}

<div class="zplus {% if not view.zplus_label.cover %}zplus--coverless{% endif %}">
    <div class="zplus__banner article__item article__item--rimless">
        {%  if view.context is zplus_content %}
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
        <div class="zplus__cover">
            {% include "zeit.web.core:templates/inc/asset/image_cover.tpl" ignore missing %}
        </div>
        {% endif %}
    </div>
</div>

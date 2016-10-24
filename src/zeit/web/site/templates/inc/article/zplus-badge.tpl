{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}

<div class="zplus {% if not view.zplus_label.cover %}zplus--coverless{% endif %}" data-ct-area="volumeteaser{% if not view.zplus_label.cover %}_coverless{% endif %}">
    <div class="zplus__banner article__item article__item--rimless" data-ct-row="0" data-ct-column="false">
        {%  if view.context is zplus_content %}
            <div class="zplus__marker">
                {{ lama.use_svg_icon('zplus', 'zplus__marker-icon svg-symbol--hide-ie', view.package, a11y=False) }}
            </div>
        {% endif %}
        <div class="zplus__text">
            <span class="zplus__label">{{ view.zplus_label.intro }}</span>
            <a href="{{ view.zplus_label.link }}" data-ct-label="exklusiv_fuer_abonnenten">
                <span class="zplus__link">{{ view.zplus_label.link_text }}</span>
                {% set packshot = view.zplus_label.cover %}
                {% include "zeit.web.core:templates/inc/asset/image_packshot.tpl" %}
            </a>
        </div>
    </div>
</div>

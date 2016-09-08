<div class="zplus">
    <div class="zplus__badge article__item article__item--rimless">
        {%  if view.context.acquisition == 'abo' %}
            <div class="zplus__marker">
                {{ lama.use_svg_icon('zplus', 'zplus__marker-icon svg-symbol--hide-ie', view.package, a11y=False) }}
            </div>
        {% endif %}
        <div class="zplus__label">
            {% if view.zplus_label %}
                <span>{{ view.zplus_label.intro }}</span>
                <a class="zplus__link" href="{{ view.zplus_label.link }}">
                    {{ view.zplus_label.link_text }}
                </a>
            {% endif %}
        </div>
    </div>
</div>

{% import 'zeit.web.site:templates/macros/centerpage_macro.tpl' as cp with context %}

<article class="{% block layout %}{{ layout }}{% endblock %}" data-video-id="{{ teaser.__name__ }}">
    <a class="{{ self.layout() }}__combined-link" href="{{ teaser | create_url }}">
        <div class="{{ self.layout() }}__container">
            {% block video_thumbnail %}
                {% set image = (teaser | get_image_group)['still.jpg'] %}
                {% include "zeit.web.site:templates/inc/teaser_asset/image_videostage.tpl" %}
            {% endblock video_thumbnail %}
            <div class="{{ self.layout() }}__inner">
                {% block playbutton %}
                    {{ cp.playbutton('block', teaser.videoDuration) }}
                {% endblock playbutton %}
                <h2 class="{{ self.layout() }}-title">
                    <span class="{{ self.layout() }}-title__kicker">
                        {{- teaser.supertitle | hide_none -}}
                    </span>
                    <span class="{{ self.layout() }}-title__title">
                        {{- teaser.teaserTitle | hide_none -}}
                    </span>
                    {% block inlineplaybutton %}
                        {{ cp.playbutton('inline', teaser.videoDuration) }}
                    {% endblock %}
                </h2>
                {% block description %}{% endblock %}
            </div>
        </div>
    </a>
</article>

{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}
{% set teaser_url = teaser | create_url %}
<article class="{% block layout %}{{ layout }}{% endblock %}" data-video-id="{{ teaser.__name__ }}"
    {% if teaser.serie and teaser.serie.serienname %} data-video-series="{{ teaser.serie.serienname | attr_safe }}"{% endif %}
    {% block data_video_size %}{% endblock %}
    data-video-provider="brightcove" {# only brightcove is used currently #}
    data-video-page-url="{{ teaser_url }}" data-meetrics="{{ area.kind }}" data-clicktracking="{{ area.kind }}">
    <a class="{{ self.layout() }}__combined-link" href="{{ teaser_url }}">
        <div class="{{ self.layout() }}__container">
            {% block teaser_media_position_before_title %}
                {% set image = get_image(module, teaser, default='wide') %}
                {% include "zeit.web.site:templates/inc/asset/image_{}.tpl".format(self.layout()) ignore missing %}
            {% endblock %}
            <div class="{{ self.layout() }}__inner">
                {% block playbutton %}
                    {{ lama.playbutton('block', teaser.videoDuration) }}
                {% endblock playbutton %}
                <h2 class="{{ self.layout() }}-title">
                    <span class="{{ self.layout() }}-title__kicker">
                        {{ teaser.supertitle | hide_none }}
                    </span>
                    <span class="{{ self.layout() }}-title__title">
                        {{ teaser.teaserTitle | hide_none }}
                    </span>
                    {% block inlineplaybutton %}
                        {{ lama.playbutton('inline', teaser.videoDuration) }}
                    {% endblock %}
                </h2>
                {% block description %}{% endblock %}
            </div>
        </div>
    </a>
</article>

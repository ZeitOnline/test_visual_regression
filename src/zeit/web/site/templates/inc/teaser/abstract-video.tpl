{% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama %}
{% set teaser_url = teaser | create_url %}
{% set duration = teaser | video_duration_format %}
<article class="{% block layout %}{{ layout }}{% endblock %}" data-video-id="{{ teaser.__name__ }}"
    {% if teaser.serie and teaser.serie.serienname %} data-video-series="{{ teaser.serie.serienname | format_webtrekk }}"{% endif %}
    {% block data_video_size %}{% endblock %}
    data-video-advertising="{{ 'withAds' if teaser.has_advertisement else 'withoutAds' }}"
    data-video-provider="brightcove" {# only brightcove is used currently #}
    data-video-page-url="{{ teaser_url }}" data-meetrics="{{ area.kind }}">
    <a class="{{ self.layout() }}__combined-link" href="{{ teaser_url }}">
        <div class="{{ self.layout() }}__container">
            {% block teaser_media_position_before_title %}
                {% set image = get_image(teaser, variant_id='wide', fallback=True) %}
                {% include "zeit.web.site:templates/inc/asset/image_{}.tpl".format(self.layout()) ignore missing %}
            {% endblock %}
            <div class="{{ self.layout() }}__inner">
                {% block playbutton %}
                    <span class="video-text-playbutton video-text-playbutton--block">
                        <span class="video-text-playbutton__text video-text-playbutton__text--block">Video ansehen</span>
                        {%- if duration %}<span class="video-text-playbutton__duration">{{ duration }}</span>{% endif %}
                    </span>
                {% endblock playbutton %}
                <h2 class="{{ self.layout() }}-title">
                    <span class="{{ self.layout() }}-title__kicker">
                        {{ teaser.supertitle }}
                    </span>
                    <span class="{{ self.layout() }}-title__title">
                        {{ teaser.teaserTitle }}
                    </span>
                    {% block inlineplaybutton %}
                        <span class="video-text-playbutton video-text-playbutton--inline">
                            <span class="video-text-playbutton__text video-text-playbutton__text--inline">Video ansehen</span>
                            {%- if duration %}<span class="video-text-playbutton__duration">{{ duration }}</span>{% endif %}
                        </span>
                    {% endblock %}
                </h2>
                {% block description %}{% endblock %}
            </div>
        </div>
    </a>
    {% block byline %}{% endblock %}
</article>

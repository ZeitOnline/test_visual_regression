<article class="{% block layout %}{{ layout }}{% endblock %}" data-video-id="xxxxxxx">
    <a class="{{ self.layout() }}__combined-link" href="{{video | create_url}}">
        <div class="{{ self.layout() }}__container">
            {% set image = (video | get_image_group)['still.jpg'] %}
            {% include "zeit.web.site:templates/inc/teaser_asset/image_videobar.tpl" %}
            <div class="video-text-playbutton video-text-playbutton--{{self.playbutton_modifier()}}">
                <span class="video-text-playbutton__text">Video ansehen</span>{{video.videoDuration | default('1:32')}}</span>
            </div>
            <h2 class="{{ self.layout() }}-title">
                <span class="{{ self.layout() }}-title__kicker">
                    {{- video.supertitle | hide_none -}}
                </span>
                <span class="{{ self.layout() }}-title__title">
                    {{- video.teaserTitle | hide_none -}}
                </span>
            </h2>
        </div>
    </a>
</article>

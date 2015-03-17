<article class="{% block layout %}{{ layout }}{% endblock %}" data-video-id="{{video.__name__}}">
    <a class="{{ self.layout() }}__combined-link" href="{{video | create_url}}">
        <div class="{{ self.layout() }}__container">
            {% block video_thumbnail %}
                {% set image = (video | get_image_group)['still.jpg'] %}
                {% include "zeit.web.site:templates/inc/teaser_asset/image_videostage.tpl" %}
            {% endblock video_thumbnail %}
            <h2 class="{{ self.layout() }}-title">
                <span class="{{ self.layout() }}-title__kicker">
                    {{- video.supertitle | hide_none -}}
                </span>
                <span class="{{ self.layout() }}-title__title">
                    {{- video.teaserTitle | hide_none -}}
                </span>
                {% block inlineplaybutton %}
                    {% set playbutton_modifier = 'inline' %}
                    {% include "zeit.web.site:templates/inc/videostage/include_playbutton.tpl" %}
                {% endblock %}
            </h2>
            {% block playbutton %}
                {% set playbutton_modifier = 'block' %}
                {% include "zeit.web.site:templates/inc/videostage/include_playbutton.tpl" %}
            {% endblock playbutton %}
        </div>
    </a>
</article>

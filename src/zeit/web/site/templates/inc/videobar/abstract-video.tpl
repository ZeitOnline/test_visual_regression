<article class="{% block layout %}{{ layout }}{% endblock %}" data-video-id="xxxxxxx">
    <a class="{{ self.layout() }}__combined-link" href="{{video | create_url}}">
        <div class="{{ self.layout() }}__container">
            <img src="{{ video.video_still | hide_none }}" alt="{{video.teaserSupertitle}} {{video.teaserTitle}}" title="Zum Abspielen des Videos anklicken" class="{{ self.layout() }}__still" />
            <div class="video-playbutton video-playbutton--small">
                <span class="video-playbutton__icon video-playbutton__icon--play video-playbutton__icon--small"></span>
                <span class="video-playbutton__time video-playbutton__time--small">1:32</span>
            </div>
        </div>
        <h2 class="{{ self.layout() }}-title">
            <span class="{{ self.layout() }}-title__kicker">
                {{- video.teaserSupertitle | hide_none -}}
            </span>
            <span class="{{ self.layout() }}-title__title">
                {{- video.teaserTitle | hide_none -}}
            </span>
        </h2>
    </a>
</article>

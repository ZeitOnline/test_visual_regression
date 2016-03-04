{% macro brightcove_video_tag(
    videoId,
    iframe=False,
    brightcove_host="//players.brightcove.net",
    brightcove_account="18140073001",
    brightcove_player="65fa926a-0fe0-4031-8cbf-9db35cecf64a",
    brightcove_embed="default"
    ) %}

<div class="video-player"
    id="video-player-{{ videoId }}"
    data-video-provider="brightcove"
    data-video-size="large">

    {% if iframe %}
        <iframe
            class="video-player__iframe"
            src='{{ brightcove_host }}/{{ brightcove_account }}/{{ brightcove_player }}_{{ brightcove_embed }}/index.html?videoId={{ videoId }}&wmode=transparent&preload=none'
            allowfullscreen webkitallowfullscreen mozallowfullscreen></iframe>
    {% else %}
        <video
            data-account="{{ brightcove_account }}"
            data-player="{{ brightcove_player }}"
            data-embed="{{ brightcove_embed }}"
            data-video-id="{{ videoId }}"
            class="video-js video-player__videotag"
            controls></video>
            <script src="{{ brightcove_host }}/{{ brightcove_account }}/{{ brightcove_player }}_{{ brightcove_embed }}/index.min.js"></script>
    {% endif %}
</div>
{% endmacro %}

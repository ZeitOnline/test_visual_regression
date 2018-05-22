{% macro brightcove_video_tag(
    videoId,
    brightcove_host="//players.brightcove.net",
    brightcove_account="18140073001",
    brightcove_player="65fa926a-0fe0-4031-8cbf-9db35cecf64a",
    brightcove_embed="default"
    ) %}

<div class="video-player" id="video-player-{{ videoId }}">
    <video
        data-account="{{ brightcove_account }}"
        data-player="{{ brightcove_player }}"
        data-embed="{{ brightcove_embed }}"
        data-video-id="{{ videoId }}"
        class="video-js video-player__videotag"
        preload="none"
        controls></video>
        <script src="{{ brightcove_host }}/{{ brightcove_account }}/{{ brightcove_player }}_{{ brightcove_embed }}/index.min.js"></script>
</div>
{% endmacro %}

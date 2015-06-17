{% macro brightcove_video_tag(
	video_id,
	iframe=False,
	expanded=False,
	brightcove_host="//players.brightcove.net",
	brightcove_account="18140073001",
	brightcove_player="65fa926a-0fe0-4031-8cbf-9db35cecf64a",
	brightcove_embed="default"
	) %}

<div class="article__item article__item--wide video-player">

	{% if iframe %}
		<iframe
			class="video-player__iframe"
			src='{{ brightcove_host }}/{{ brightcove_account }}/{{ brightcove_player }}_{{ brightcove_embed }}/index.html?videoId={{ video_id }}&wmode=transparent'
			allowfullscreen webkitallowfullscreen mozallowfullscreen></iframe>
	{% else %}
	    <video
	        data-account="{{ brightcove_account }}"
	        data-player="{{ brightcove_player }}"
	        data-embed="{{ brightcove_embed }}"
	        data-video-id="{{ video_id }}"
	        class="video-js video-player__videotag"
	        controls></video>
	    <script src="{{ brightcove_host }}/{{ brightcove_account }}/{{ brightcove_player }}_{{ brightcove_embed }}/index.min.js"></script>
	{% endif %}

</div>
{% endmacro %}

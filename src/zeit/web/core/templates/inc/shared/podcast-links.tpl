{% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama %}
{% set itunes_id = podcast['itunes_id'] %}
{% set deezer_url = podcast['deezer_url'] %}
{% set spotify_url = podcast['spotify_url'] %}
{% set alexa_url = podcast['alexa_url'] %}

<ul class="podcastfooter__platforms podcast-links">
    {% if itunes_id %}
    <li class="podcast-links__item">
        <a class="podcast-links__link" href="{{ settings('itunes_podcast_base_url') ~ itunes_id }}" title="Podcast bei iTunes">{{ lama.use_svg_icon('itunes', 'itunes__icon', view.package, a11y=False, remove_title=True) }}</a>
    </li>
    {% endif %}
    {% if spotify_url %}
    <li class="podcast-links__item">
        <a class="podcast-links__link" href="{{ spotify_url }}" title="Podcast bei Spotify">{{ lama.use_svg_icon('spotify', 'spotify__icon', view.package, a11y=False, remove_title=True) }}</a>
    </li>
    {% endif %}
    {% if deezer_url %}
    <li class="podcast-links__item">
        <a class="podcast-links__link" href="{{ deezer_url }}" title="Podcast bei Deezer">{{ lama.use_svg_icon('deezer', 'deezer__icon', view.package, a11y=False, remove_title=True) }}</a>
    </li>
    {% endif %}
    {% if alexa_url %}
    <li class="podcast-links__item">
        <a class="podcast-links__link" href="{{ alexa_url }}" title="Podcast auf Alexa">{{ lama.use_svg_icon('alexaskill', 'alexa__icon', view.package, a11y=False, remove_title=True) }}</a>
    </li>
    {% endif %}
</ul>

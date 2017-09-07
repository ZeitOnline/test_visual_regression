{# Teaser layout for referencing an article that contains a podcast module #}
{% set teaser_jsonname = teaser.uniqueId | format_only_varchars %}
<div class="teaser-podcast">
  {% set IPodcast = 'zeit.content.article.edit.interfaces.IPodcast' %}
  {% set IBlock = 'zeit.web.core.interfaces.IFrontendBlock' %}
  {% if provides(teaser.header.module, IPodcast) %}
    {% set module = adapt(teaser.header.module, IBlock) %}
  {% else %}
    {% set module = adapt(teaser.body.find_first(resolve(IPodcast)), IBlock) %}
  {% endif %}

  {% set podcast_player_theme = settings('podcast_theme_cp') %}
  {% include "zeit.web.core:templates/inc/podcast_player.html" %}


    <div class="teaser-podcast__sharing">
        {% if module.podlove_configuration %}
            <script type="text/javascript">
                window.podcastData_{{ teaser_jsonname }} = {{ module.podlove_configuration | tojson | safe }};
            </script>
            <div class="teaser-podcast__sharing-podlove">
                <script class="podlove-subscribe-button" src="https://cdn.podlove.org/subscribe-button/javascripts/app.js" data-language="de" data-color="#000" data-size="small" data-style="outline" data-json-data="podcastData_{{ teaser_jsonname }}" async defer></script>
            </div>
        {% endif %}
        <a class="teaser-podcast__sharing-link" href="{{ context | find_series_cp | create_url }}">Alle Folgen</a>
    </div>

</div>

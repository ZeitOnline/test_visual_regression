{# Teaser layout for referencing an article that contains a podcast module #}
<div class="podcast">
  {% set IPodcast = 'zeit.content.article.edit.interfaces.IPodcast' %}
  {% set IBlock = 'zeit.web.core.interfaces.IFrontendBlock' %}
  {% if provides(teaser.header.module, IPodcast) %}
    {% set module = adapt(teaser.header.module, IBlock) %}
  {% else %}
    {% set module = adapt(teaser.body.find_first(resolve(IPodcast)), IBlock) %}
  {% endif %}

  {% set podcast_player_theme = settings('podcast_theme_cp') %}
  {% include "zeit.web.core:templates/inc/podcast_player.html" %}
</div>

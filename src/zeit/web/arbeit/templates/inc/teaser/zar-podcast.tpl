{# Teaser layout for referencing an article that contains a podcast module #}
<div class="teaser-podcast">
  {% set module_id = module.__name__ | format_iqd %}
  {% set IPodcast = 'zeit.content.article.edit.interfaces.IPodcast' %}
  {% set IModule = 'zeit.web.core.interfaces.IArticleModule' %}
  {% if provides(teaser.header.module, IPodcast) %}
    {% set module = adapt(teaser.header.module, IModule) %}
  {% else %}
    {% set module = adapt(teaser.body.find_first(resolve(IPodcast)), IModule) %}
  {% endif %}

  {% set podcast_player_id = module_id %}
  {% set podcast_player_theme = settings('podcast_theme_cp') %}
  {% include "zeit.web.core:templates/inc/podcast_player.html" %}

  {% set podcastfooter_additional_class = "teaser-podcast-footer" %}
  {% include "zeit.web.core:templates/inc/shared/podcastfooter-for-teasers.tpl" %}

</div>

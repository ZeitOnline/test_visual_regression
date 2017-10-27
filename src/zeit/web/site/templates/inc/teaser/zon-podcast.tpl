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


    <div class="teaser-podcast-footer podcastfooter">

        {% set podlove_button_id = module_id %}
        {% set podlove_button_configuration = module.podlove_configuration %}
        {% include "zeit.web.core:templates/inc/shared/podlove-button.tpl" %}

        {% set podcast = module.podcast %}
        {% include "zeit.web.core:templates/inc/shared/podcast-links.tpl" %}

        {% if teaser.serie %}
        <span>
            <a class="teaser-podcast-footer__link podcastfooter__serieslink" href="{{ teaser | find_series_cp | create_url }}">Alle Folgen</a>
        </span>
        {% endif %}
    </div>

</div>

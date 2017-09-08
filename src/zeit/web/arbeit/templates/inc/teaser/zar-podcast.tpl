{# Teaser layout for referencing an article that contains a podcast module #}
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


    <div class="teaser-podcast-footer">

        {% set podlove_button_id = '{}__{}'.format(teaser.uniqueId, area.uniqueId) | format_only_varchars %}
        {% set podlove_button_configuration = module.podlove_configuration %}
        {% include "zeit.web.core:templates/inc/shared/podlove-button.html" %}

        <span>
            <a class="teaser-podcast-footer__link" href="{{ context | find_series_cp | create_url }}">Alle Folgen</a>
        </span>
    </div>

</div>

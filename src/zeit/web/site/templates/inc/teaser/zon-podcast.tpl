{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}
{# Teaser layout for referencing an article that contains a podcast module #}
{% set teaser_jsonname = '{}__{}'.format(teaser.uniqueId, area.uniqueId) | format_only_varchars %}
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
        {% if module.podlove_configuration %}
            <script type="text/javascript">
                window.podcastData_{{ teaser_jsonname }} = {{ module.podlove_configuration | tojson | safe }};
            </script>
            {# Podlove verträgt es derzeit nicht, wenn der Button ein Link ist.
               Das wäre mal einen Pull Request in deren Software wert!
               Und dann können wir das hier nutzen:
                {% set external_site_url = view.header_module.podlove_configuration.external_site_url or 'http://{}.podigee.io'.format(view.header_module.podlove_configuration.podigee_subdomain) %}
               Und dann auch cursor:pointer sowie no-js aus dem CSS entfernen!
            #}
            <span class="podlove-button podlove-subscribe-button-{{ teaser_jsonname }}">
                {{ lama.use_svg_icon('podcast', 'podlove-button__icon', view.package, a11y=False) }}
                Abonnieren
            </span>
            <script class="podlove-subscribe-button" src="https://cdn.podlove.org/subscribe-button/javascripts/app.js" data-language="de"data-size="small" data-hide="true" data-buttonid="{{ teaser_jsonname }}" data-json-data="podcastData_{{ teaser_jsonname }}" async defer></script>
            {# Attention: The data-size attribute is needed, even though we use our own button. Otherwise the podlove script fails. #}
        {% endif %}
        <span>
            <a class="teaser-podcast-footer__link" href="{{ context | find_series_cp | create_url }}">Alle Folgen</a>
        </span>
    </div>

</div>

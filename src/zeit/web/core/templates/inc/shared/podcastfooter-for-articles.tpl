<div class="podcastfooter {{ podcastfooter_additional_class }}">

    {% set podlove_button_id = view.header_module.context.episode_id %}
    {% set podlove_button_configuration = view.header_module.podlove_configuration %}
    {% include "zeit.web.core:templates/inc/shared/podlove-button.tpl" %}

    {% set podcast = view.header_module.podcast %}
    {% include "zeit.web.core:templates/inc/shared/podcast-links.tpl" %}

    {%- if view.serie -%}
        <a href="{{ context | find_series_cp | create_url }}" class="podcastfooter__serieslink">Alle Folgen</a>
    {%- endif -%}
</div>

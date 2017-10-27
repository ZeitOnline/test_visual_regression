<div class="podcastfooter {{ podcastfooter_additional_class }}">

    {% set podlove_button_id = module_id %}
    {% set podlove_button_configuration = module.podlove_configuration %}
    {% include "zeit.web.core:templates/inc/shared/podlove-button.tpl" %}

    {% set podcast = module.podcast %}
    {% include "zeit.web.core:templates/inc/shared/podcast-links.tpl" %}

    {% if teaser.serie %}
        <a class="teaser-podcast-footer__link podcastfooter__serieslink" href="{{ teaser | find_series_cp | create_url }}">Alle Folgen</a>
    {% endif %}
</div>

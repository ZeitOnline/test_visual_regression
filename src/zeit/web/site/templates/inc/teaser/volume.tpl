{% set volume = teaser %}
{% set linklabel = module.read_more or 'Lesen Sie diese Ausgabe als E-Paper, App und auf dem E-Reader.' %}
<div class="volume-navigation" data-ct-area="volumeteaser" data-ct-row="{{ region_loop.index }}">
    <a class="volume-navigation__current" href="https://epaper.zeit.de/abo/diezeit/{{ volume.year }}/{{ '%02d' % volume.volume }}" title="{{ linklabel }}" data-ct-label="{{ linklabel }}">
        <span class="volume-navigation__packshot">
            {% set packshot = volume.covers['printcover'] %}
            {% set packshot_layout = 'volume-navigation' %}
            {% include "zeit.web.core:templates/inc/asset/image_packshot.tpl" %}
        </span>
        <span class="volume-navigation__cta">
            <span class="volume-navigation__link">
            {{ linklabel }}
            </span>
        </span>
    </a>
</div>

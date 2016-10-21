{% for block in area.values()-%}
    {% set volume = block | first_child %}
    {% set href = 'https://zeit.de/{0}/{1:02d}/index?wt_params=foo42'.format(volume.year, volume.volume) %}
    {% set packshot = volume.covers['printcover'] %}
    {% set packshot_layout = module_layout %}
    {% set packshot_fallback = volume.covers['printcover_fallback'] %}
    {% set tracking_slug = "volume-overview-teaser..{}.".format(loop.index) %}

    <a class="volume-overview-teaser__wrapper" href="{{ href }}" data-id="{{ tracking_slug }}">
        {% include "zeit.web.core:templates/inc/asset/image_packshot.tpl" ignore missing %}
        <figcaption class="volume-overview-teaser__caption">
            <p class="{{ module_layout }}__issue">{{ '%02d' % volume.volume }}/{{ volume.year }}</p>
            <span class="{{ module_layout }}__cta" href="{{ href }}">Jetzt lesen</span>
        </figcaption>
    </a>
{% endfor %}

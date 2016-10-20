{% for block in area.values()-%}
    {% set volume = block | first_child %}
    {% set href = 'https://zeit.de/{0}/{1:02d}/index?wt_params=foo42'.format(volume.year, volume.volume) %}
    {% set packshot = volume.covers['printcover'] %}
    {% set packshot_layout = module_layout %}
    {% set packshot_fallback = volume.covers['printcover_fallback'] %}
    {% set tracking_slug = "volume-overview-teaser..{}.".format(loop.index) %}

    <a class="volume-overview-teaser__media" href="{{ href }}">
        <div class="volume-overview-teaser__media-container">
        {% include "zeit.web.core:templates/inc/asset/image_packshot.tpl".format(view.package) ignore missing %}
        </div>
        <div class="class=volume-overview-teaser__caption">
            <p class="{{ module_layout }}__issue">{{ '%02d' % volume.volume }}/{{ volume.year }}</p>
            <a class="{{ module_layout }}__link" href="{{ href }}" data-id="{{ tracking_slug }}text">Jetzt lesen</a>
        </div>
    </a>
{% endfor %}

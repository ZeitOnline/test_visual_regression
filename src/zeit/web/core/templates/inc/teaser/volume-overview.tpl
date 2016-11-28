{% for block in area.values()-%}
    {% set volume = block | first_child %}
    {% set href = '{0}{1}/{2:02d}/index'.format(request.route_url('home'), volume.year, volume.volume) %}
    {% set packshot = volume.covers['printcover'] %}
    {% set packshot_layout = module_layout %}
    {% set tracking_slug = "volume-overview-teaser..{}.{}_{}".format(loop.index, '%02d' % volume.volume, volume.year) %}

    <a class="volume-overview-teaser__wrapper" href="{{ href }}" data-id="{{ tracking_slug }}">
        {% include "zeit.web.core:templates/inc/asset/image_packshot.tpl" %}
        <div class="volume-overview-teaser__caption">
            <p class="{{ module_layout }}__issue">{{ '%02d' % volume.volume }}/{{ volume.year }}</p>
            <span class="{{ module_layout }}__cta"><span>Jetzt </span><span class="visually-hidden">Ausgabe {{ '%02d' % volume.volume }}/{{ volume.year }} </span> <span>lesen</span>
        </div>
    </a>
{% endfor %}

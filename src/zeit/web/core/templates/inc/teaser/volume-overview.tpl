{% set volume = module | first_child %}
{% set layout = 'teaser-{}'.format(module | get_layout) %}
{% set href = '{0}{1}/{2:02d}/index'.format(request.route_url('home'), volume.year, volume.volume) %}
{% set packshot = volume.covers['printcover'] %}
{% set module_layout = layout %}

<aside class="{{ layout }}">
    <a class="{{ layout }}__link" href="{{ href }}" data-ct-label="{{ '%02d_%d' | format(volume.volume, volume.year) }}">
        {% include "zeit.web.core:templates/inc/asset/image_packshot.tpl" %}
        <div class="{{ layout }}__caption">
            <p class="{{ layout }}__issue"><strong>{{ '%02d/%d' | format (volume.volume, volume.year) }}</strong></p>
            <span class="{{ layout }}__cta">
                Jetzt <span class="visually-hidden">Ausgabe {{ '%02d/%d' | format (volume.volume, volume.year) }}</span> lesen
            </span>
        </div>
    </a>
</aside>

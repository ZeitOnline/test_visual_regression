{% for block in area.values()-%}
    {% set volume = block | first_child %}
    {% set tracking_slug = "volume-overview-teaser..{}.".format(loop.index) %}
    {% include "{}:templates/inc/asset/image_volume-overview.tpl".format(view.package) ignore missing %}
{% endfor %}

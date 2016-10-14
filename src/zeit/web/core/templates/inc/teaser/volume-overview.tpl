{% for block in area.values()-%}
    {% set volume = block | first_child %}
    {% include "{}:templates/inc/asset/image_volume-overview.tpl".format(view.package) ignore missing %}
{% endfor %}

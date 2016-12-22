{% if view.header_module and view.page_nr == 1 %}
    {% set block = view.header_module -%}
    {% set type = block | block_type -%}
    <div data-ct-row="{{ type }}">
    {% include [
        "{0}:templates/inc/blocks/{1}_{2}.html".format(view.package, type, block.layout),
        "{0}:templates/inc/blocks/{1}.html".format(view.package, type),
        "zeit.web.core:templates/inc/blocks/{0}_{1}.html".format(type, block.layout),
        "zeit.web.core:templates/inc/blocks/{0}.html".format(type)] ignore missing -%}
    </div>
{% endif %}

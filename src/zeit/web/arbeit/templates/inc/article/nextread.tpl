{% if module %}
    {% set teaser = module | first_child %}
    {% set teaser_type = teaser | block_type %}
    {% include
        ["zeit.web.arbeit:templates/inc/article/nextread/{}.tpl".format(teaser_type),
        "zeit.web.arbeit:templates/inc/article/nextread/default.tpl"] %}
{% endif %}

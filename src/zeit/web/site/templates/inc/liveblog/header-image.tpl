{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}
{% set image = view.header_module if is_instance(view.header_module, 'zeit.web.core.block.Image') else None %}
{% set module_layout = "article-heading" %}

{% extends "zeit.web.core:templates/inc/asset/image_linked.tpl" %}

{% set image = get_image(packshot, fallback=False) or get_image(packshot_fallback, fallback=False) %}

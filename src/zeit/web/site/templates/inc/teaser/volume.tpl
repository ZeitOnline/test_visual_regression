{%- extends "zeit.web.core:templates/inc/teaser/abstract-volume.tpl" -%}

{% set volume = teaser %}
{% set linklabel = module.read_more or 'Lesen Sie diese Ausgabe als E-Paper, App und auf dem E-Reader.' %}

{% block volumeteaser_link %}{{settings('volume_navigation_base') | format(volume.year, volume.volume)}}{% endblock %}

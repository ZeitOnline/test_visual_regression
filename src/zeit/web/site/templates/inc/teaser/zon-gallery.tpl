{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-gallery{% endblock %}
{% block teaser_attributes %} data-type="teaser"{% endblock %}

{% block teaser_journalistic_format %}{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/imagegroup_gallery.tpl" %}
{% endblock %}

{% block kicker_logo %}
    {% set logo_layout = self.layout() %}
    {% for template in teaser | logo_icon(area.kind, zplus_only=True) %}
        {% include "zeit.web.core:templates/inc/badges/{}.tpl".format(template) %}
    {% endfor %}
{% endblock %}

{# Eliminate default teaser metadata #}
{% block teaser_metadata_default %}{% endblock %}
{# Eliminate default teaser byline #}
{% block teaser_byline %}{% endblock %}

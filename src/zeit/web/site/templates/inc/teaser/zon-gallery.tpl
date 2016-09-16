{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-gallery{% endblock %}
{% block teaser_attributes %}data-type="teaser"{% endblock %}

{% block teaser_journalistic_format %}{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/imagegroup_gallery.tpl" %}
{% endblock %}

{% block kicker_logo %}
    {{ self.zplus_kicker_logo() }}
{% endblock %}

{# Eliminate default teaser metadata #}
{% block teaser_metadata_default %}{% endblock %}
{# Eliminate default teaser byline #}
{% block teaser_byline %}{% endblock %}

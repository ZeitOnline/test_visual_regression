{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-zett{% endblock %}
{% block teaser_journalistic_format %}{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/asset/image_teaser.tpl" ignore missing %}
{% endblock %}

{% block teaser_kicker %}{% endblock %}
{% block teaser_container %}{% endblock %}
{# Eliminate default teaser metadata #}
{% block teaser_metadata_default %}{% endblock %}
{# Eliminate default teaser byline #}
{% block teaser_byline %}{% endblock %}

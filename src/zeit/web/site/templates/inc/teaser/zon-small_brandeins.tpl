{% extends "zeit.web.site:templates/inc/teaser/zon-small.tpl" %}

{% block layout %}{% if loop.index == 1 %}teaser-large{% else %}teaser-small{% endif %}{% endblock %}

{% block teaser_kicker %}
    <span class="{{ '%s__kicker' | format(self.layout()) | with_mods('brandeins-parquet') }}">
        {{- teaser.teaserSupertitle or teaser.supertitle -}}
    </span>
    {%- if teaser.teaserSupertitle or teaser.supertitle -%}
        <span class="visually-hidden">:</span>
    {% endif %}
{% endblock %}

{% block teaser_label %}
    {% if module[0].is_ad %}
        <span class="{{ self.layout() }}__label">Anzeige</span>
    {% endif %}
{% endblock %}

{% block teaser_media_position_after_title %}
    {% if loop.index == 1 %}
        {% set module_layout = self.layout() %}
        {% include "zeit.web.core:templates/inc/asset/image_teaser.tpl" %}
    {% endif %}
{% endblock %}
{% block teaser_media_position_before_title %}
    {% if loop.index > 1 %}
        {% set module_layout = self.layout() %}
        {% include "zeit.web.core:templates/inc/asset/image_teaser.tpl" %}
    {% endif %}
{% endblock %}
